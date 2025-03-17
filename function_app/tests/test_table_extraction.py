"""
Tests for the table extraction module.

This module contains tests for the TableExtractor class and related functionality.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from services.document_intelligence.table_extraction import (
    TableExtractor,
    create_table_extractor
)
from services.document_intelligence.client import DocumentIntelligenceClient


class TestTableExtractor(unittest.TestCase):
    """Tests for the TableExtractor class."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock client
        self.mock_client = MagicMock(spec=DocumentIntelligenceClient)
        
        # Create a TableExtractor with the mock client
        self.extractor = TableExtractor(self.mock_client)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.extractor.client, self.mock_client)
    
    def test_extract_tables(self):
        """Test extracting tables from a document."""
        # Mock the analyze_document method of the client
        mock_result = {
            "analyze_result": {
                "tables": [
                    {
                        "row_count": 3,
                        "column_count": 2,
                        "cells": [
                            {
                                "row_index": 0,
                                "column_index": 0,
                                "content": "Header 1",
                                "confidence": 0.95
                            },
                            {
                                "row_index": 0,
                                "column_index": 1,
                                "content": "Header 2",
                                "confidence": 0.95
                            },
                            {
                                "row_index": 1,
                                "column_index": 0,
                                "content": "Cell 1,1",
                                "confidence": 0.9
                            },
                            {
                                "row_index": 1,
                                "column_index": 1,
                                "content": "Cell 1,2",
                                "confidence": 0.9
                            },
                            {
                                "row_index": 2,
                                "column_index": 0,
                                "content": "Cell 2,1",
                                "confidence": 0.85
                            },
                            {
                                "row_index": 2,
                                "column_index": 1,
                                "content": "Cell 2,2",
                                "confidence": 0.85
                            }
                        ],
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [100, 100, 300, 100, 300, 200, 100, 200]
                            }
                        ],
                        "confidence": 0.9
                    }
                ]
            }
        }
        self.mock_client.analyze_document.return_value = mock_result
        
        # Call the method to test
        result = self.extractor.extract_tables(b"test document")
        
        # Verify the client was called correctly
        self.mock_client.analyze_document.assert_called_once_with(b"test document", model_id="prebuilt-layout")
        
        # Verify the result
        self.assertEqual(len(result["tables"]), 1)
        self.assertEqual(result["table_count"], 1)
        self.assertEqual(result["tables"][0]["row_count"], 3)
        self.assertEqual(result["tables"][0]["column_count"], 2)
        self.assertEqual(result["tables"][0]["confidence"], 0.9)
        self.assertEqual(result["tables"][0]["page_number"], 1)
        
        # Verify the table content
        rows = result["tables"][0]["rows"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(rows[0]), 2)
        self.assertEqual(rows[0][0], "Header 1")
        self.assertEqual(rows[0][1], "Header 2")
        self.assertEqual(rows[1][0], "Cell 1,1")
        self.assertEqual(rows[1][1], "Cell 1,2")
        self.assertEqual(rows[2][0], "Cell 2,1")
        self.assertEqual(rows[2][1], "Cell 2,2")
    
    def test_extract_tables_empty(self):
        """Test extracting tables from a document with no tables."""
        # Mock the analyze_document method of the client
        mock_result = {
            "analyze_result": {}
        }
        self.mock_client.analyze_document.return_value = mock_result
        
        # Call the method to test
        result = self.extractor.extract_tables(b"test document")
        
        # Verify the result
        self.assertEqual(len(result["tables"]), 0)
        self.assertEqual(result["table_count"], 0)
    
    def test_organize_table_cells(self):
        """Test organizing table cells into a 2D array."""
        # Create a mock table
        table = {
            "cells": [
                {
                    "row_index": 0,
                    "column_index": 0,
                    "content": "Header 1"
                },
                {
                    "row_index": 0,
                    "column_index": 1,
                    "content": "Header 2"
                },
                {
                    "row_index": 1,
                    "column_index": 0,
                    "content": "Cell 1,1"
                },
                {
                    "row_index": 1,
                    "column_index": 1,
                    "content": "Cell 1,2"
                }
            ]
        }
        
        # Call the method to test
        rows = self.extractor._organize_table_cells(table)
        
        # Verify the result
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[0]), 2)
        self.assertEqual(rows[0][0], "Header 1")
        self.assertEqual(rows[0][1], "Header 2")
        self.assertEqual(rows[1][0], "Cell 1,1")
        self.assertEqual(rows[1][1], "Cell 1,2")
    
    def test_organize_table_cells_with_spans(self):
        """Test organizing table cells with row and column spans."""
        # Create a mock table with spans
        table = {
            "cells": [
                {
                    "row_index": 0,
                    "column_index": 0,
                    "content": "Header 1"
                },
                {
                    "row_index": 0,
                    "column_index": 1,
                    "content": "Header 2"
                },
                {
                    "row_index": 1,
                    "column_index": 0,
                    "content": "Cell 1,1",
                    "row_span": 2  # Spans 2 rows
                },
                {
                    "row_index": 1,
                    "column_index": 1,
                    "content": "Cell 1,2"
                },
                {
                    "row_index": 2,
                    "column_index": 1,
                    "content": "Cell 2,2"
                }
            ]
        }
        
        # Call the method to test
        rows = self.extractor._organize_table_cells(table)
        
        # Verify the result
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(rows[0]), 2)
        self.assertEqual(rows[0][0], "Header 1")
        self.assertEqual(rows[0][1], "Header 2")
        self.assertEqual(rows[1][0], "Cell 1,1")
        self.assertEqual(rows[1][1], "Cell 1,2")
        self.assertEqual(rows[2][0], "Cell 1,1")  # Same content due to row span
        self.assertEqual(rows[2][1], "Cell 2,2")
    
    def test_organize_table_cells_empty(self):
        """Test organizing table cells with no cells."""
        # Create a mock table with no cells
        table = {}
        
        # Call the method to test
        rows = self.extractor._organize_table_cells(table)
        
        # Verify the result
        self.assertEqual(rows, [])
    
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


class TestCreateTableExtractor(unittest.TestCase):
    """Tests for the create_table_extractor function."""
    
    def test_create_extractor(self):
        """Test creating a TableExtractor."""
        # Create a mock client
        mock_client = MagicMock(spec=DocumentIntelligenceClient)
        
        # Call the function to test
        extractor = create_table_extractor(mock_client)
        
        # Verify the result
        self.assertIsInstance(extractor, TableExtractor)
        self.assertEqual(extractor.client, mock_client)


if __name__ == "__main__":
    unittest.main()
