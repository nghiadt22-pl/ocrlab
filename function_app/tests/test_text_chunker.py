"""
Tests for the Text Chunker module.

This module contains tests for the TextChunker class and related functionality.
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
from services.vector_search.text_chunker import (
    TextChunker,
    create_text_chunker
)


class TestTextChunker(unittest.TestCase):
    """Tests for the TextChunker class."""

    def setUp(self):
        """Set up test environment."""
        self.chunker = TextChunker()
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        chunker = TextChunker()
        self.assertEqual(chunker.chunk_size, 1000)
        self.assertEqual(chunker.chunk_overlap, 200)
        self.assertEqual(chunker.separator, " ")
    
    def test_init_with_params(self):
        """Test initialization with custom parameters."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100, separator="\n")
        self.assertEqual(chunker.chunk_size, 500)
        self.assertEqual(chunker.chunk_overlap, 100)
        self.assertEqual(chunker.separator, "\n")
    
    def test_chunk_text_short(self):
        """Test chunking short text that fits in a single chunk."""
        text = "This is a short text that should fit in a single chunk."
        chunks = self.chunker.chunk_text(text)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["content"], text)
        self.assertEqual(chunks[0]["metadata"]["chunk_index"], 0)
        self.assertEqual(chunks[0]["metadata"]["total_chunks"], 1)
    
    def test_chunk_text_long(self):
        """Test chunking long text that spans multiple chunks."""
        # Create a long text
        words = ["word"] * 1200  # More than chunk_size (1000)
        text = " ".join(words)
        
        chunks = self.chunker.chunk_text(text)
        
        # Verify we have multiple chunks
        self.assertGreater(len(chunks), 1)
        
        # Verify each chunk has the correct metadata
        for i, chunk in enumerate(chunks):
            self.assertEqual(chunk["metadata"]["chunk_index"], i)
            self.assertEqual(chunk["metadata"]["total_chunks"], len(chunks))
            
            # Verify chunk size (except possibly the last chunk)
            if i < len(chunks) - 1:
                self.assertLessEqual(len(chunk["content"].split()), self.chunker.chunk_size)
            
            # Verify overlap with next chunk
            if i < len(chunks) - 1:
                current_words = chunk["content"].split()
                next_words = chunks[i + 1]["content"].split()
                
                # The last words of the current chunk should match the first words of the next chunk
                overlap_size = min(self.chunker.chunk_overlap, len(current_words), len(next_words))
                current_last_words = current_words[-overlap_size:]
                next_first_words = next_words[:overlap_size]
                
                self.assertEqual(current_last_words, next_first_words)
    
    def test_chunk_text_with_metadata(self):
        """Test chunking text with metadata."""
        text = "This is a text with metadata."
        metadata = {"source": "test", "page_number": 1}
        
        chunks = self.chunker.chunk_text(text, metadata)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["content"], text)
        self.assertEqual(chunks[0]["metadata"]["source"], "test")
        self.assertEqual(chunks[0]["metadata"]["page_number"], 1)
        self.assertEqual(chunks[0]["metadata"]["chunk_index"], 0)
        self.assertEqual(chunks[0]["metadata"]["total_chunks"], 1)
    
    def test_chunk_document_empty(self):
        """Test chunking an empty document."""
        document = {"paragraphs": []}
        
        chunks = self.chunker.chunk_document(document)
        
        self.assertEqual(len(chunks), 0)
    
    def test_chunk_document_simple(self):
        """Test chunking a simple document with paragraphs."""
        document = {
            "paragraphs": [
                {"content": "This is paragraph 1.", "page_number": 1},
                {"content": "This is paragraph 2.", "page_number": 1},
                {"content": "This is paragraph 3.", "page_number": 2}
            ]
        }
        
        chunks = self.chunker.chunk_document(document)
        
        # For this simple document, we should have one chunk
        self.assertEqual(len(chunks), 1)
        self.assertIn("This is paragraph 1.", chunks[0]["content"])
        self.assertIn("This is paragraph 2.", chunks[0]["content"])
        self.assertIn("This is paragraph 3.", chunks[0]["content"])
        self.assertEqual(chunks[0]["metadata"]["chunk_index"], 0)
        self.assertEqual(chunks[0]["metadata"]["total_chunks"], 1)
    
    def test_chunk_document_complex(self):
        """Test chunking a complex document with paragraphs, tables, and handwriting."""
        # Create a document with various content types
        document = {
            "paragraphs": [
                {"content": "This is paragraph 1.", "page_number": 1},
                {"content": "This is paragraph 2.", "page_number": 1}
            ],
            "tables": [
                {
                    "content": "Table 1 content",
                    "page_number": 1,
                    "rows": 2,
                    "columns": 2
                }
            ],
            "handwritten_items": [
                {
                    "content": "Handwritten note 1",
                    "page_number": 2,
                    "confidence": 0.9
                }
            ]
        }
        
        chunks = self.chunker.chunk_document(document)
        
        # Verify we have at least one chunk
        self.assertGreaterEqual(len(chunks), 1)
        
        # Verify the content includes all document elements
        all_content = " ".join([chunk["content"] for chunk in chunks])
        self.assertIn("This is paragraph 1.", all_content)
        self.assertIn("This is paragraph 2.", all_content)
        self.assertIn("Table 1 content", all_content)
        self.assertIn("Handwritten note 1", all_content)
        
        # Verify metadata
        for i, chunk in enumerate(chunks):
            self.assertEqual(chunk["metadata"]["chunk_index"], i)
            self.assertEqual(chunk["metadata"]["total_chunks"], len(chunks))
    
    def test_chunk_by_page(self):
        """Test chunking a document by page."""
        # Create a document with content on multiple pages
        document = {
            "paragraphs": [
                {"content": "This is paragraph 1 on page 1.", "page_number": 1},
                {"content": "This is paragraph 2 on page 1.", "page_number": 1},
                {"content": "This is paragraph 1 on page 2.", "page_number": 2},
                {"content": "This is paragraph 2 on page 2.", "page_number": 2}
            ]
        }
        
        chunker = TextChunker(chunk_by_page=True)
        chunks = chunker.chunk_document(document)
        
        # We should have two chunks, one for each page
        self.assertEqual(len(chunks), 2)
        
        # Verify page 1 content
        self.assertIn("This is paragraph 1 on page 1.", chunks[0]["content"])
        self.assertIn("This is paragraph 2 on page 1.", chunks[0]["content"])
        self.assertEqual(chunks[0]["metadata"]["page_number"], 1)
        
        # Verify page 2 content
        self.assertIn("This is paragraph 1 on page 2.", chunks[1]["content"])
        self.assertIn("This is paragraph 2 on page 2.", chunks[1]["content"])
        self.assertEqual(chunks[1]["metadata"]["page_number"], 2)


class TestCreateTextChunker(unittest.TestCase):
    """Tests for the create_text_chunker function."""

    def test_create_text_chunker_with_defaults(self):
        """Test creating a TextChunker with default parameters."""
        chunker = create_text_chunker()
        
        self.assertIsInstance(chunker, TextChunker)
        self.assertEqual(chunker.chunk_size, 1000)
        self.assertEqual(chunker.chunk_overlap, 200)
        self.assertEqual(chunker.separator, " ")
        self.assertFalse(chunker.chunk_by_page)
    
    def test_create_text_chunker_with_params(self):
        """Test creating a TextChunker with custom parameters."""
        chunker = create_text_chunker(
            chunk_size=500,
            chunk_overlap=100,
            separator="\n",
            chunk_by_page=True
        )
        
        self.assertIsInstance(chunker, TextChunker)
        self.assertEqual(chunker.chunk_size, 500)
        self.assertEqual(chunker.chunk_overlap, 100)
        self.assertEqual(chunker.separator, "\n")
        self.assertTrue(chunker.chunk_by_page)


if __name__ == "__main__":
    unittest.main() 