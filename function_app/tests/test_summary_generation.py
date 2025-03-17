"""
Tests for the summary generation module.

This module contains tests for the SummaryGenerator class and related functionality.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from services.document_intelligence.summary_generation import (
    SummaryGenerator,
    create_summary_generator
)


class TestSummaryGenerator(unittest.TestCase):
    """Tests for the SummaryGenerator class."""

    def setUp(self):
        """Set up test environment."""
        # Create a SummaryGenerator
        self.generator = SummaryGenerator(max_summary_length=3)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.generator.max_summary_length, 3)
    
    def test_generate_summary(self):
        """Test generating a summary from document content."""
        # Create mock document content
        document_content = {
            "paragraphs": [
                {
                    "content": "This is the first paragraph of the document. It contains important information about the topic.",
                    "confidence": 0.95
                },
                {
                    "content": "This is the second paragraph. It provides additional details and context.",
                    "confidence": 0.9
                },
                {
                    "content": "This is the third paragraph. It discusses some related concepts and ideas.",
                    "confidence": 0.85
                },
                {
                    "content": "This is the fourth paragraph. It contains less important information.",
                    "confidence": 0.8
                },
                {
                    "content": "This is the fifth paragraph. It concludes the document with a summary.",
                    "confidence": 0.75
                }
            ],
            "document_type": "article",
            "language": "en",
            "page_count": 1
        }
        
        # Call the method to test
        result = self.generator.generate_summary(document_content)
        
        # Verify the result
        self.assertIn("summary", result)
        self.assertIn("keywords", result)
        self.assertEqual(result["document_type"], "article")
        self.assertEqual(result["language"], "en")
        self.assertEqual(result["page_count"], 1)
        
        # Verify the summary is not empty
        self.assertNotEqual(result["summary"], "")
        
        # Verify the summary contains at most 3 sentences (max_summary_length)
        sentences = result["summary"].split(". ")
        self.assertLessEqual(len(sentences), 3)
        
        # Verify keywords are extracted
        self.assertGreater(len(result["keywords"]), 0)
    
    def test_generate_summary_empty_document(self):
        """Test generating a summary from an empty document."""
        # Create mock empty document content
        document_content = {
            "paragraphs": [],
            "document_type": "unknown",
            "language": "unknown",
            "page_count": 0
        }
        
        # Call the method to test
        result = self.generator.generate_summary(document_content)
        
        # Verify the result
        self.assertEqual(result["summary"], "")
        self.assertEqual(result["keywords"], [])
        self.assertEqual(result["document_type"], "unknown")
        self.assertEqual(result["language"], "unknown")
        self.assertEqual(result["page_count"], 0)
    
    def test_extract_text_from_document(self):
        """Test extracting text from document content."""
        # Create mock document content with different types of content
        document_content = {
            "paragraphs": [
                {"content": "Paragraph 1"},
                {"content": "Paragraph 2"}
            ],
            "tables": [
                {
                    "rows": [
                        ["Header 1", "Header 2"],
                        ["Cell 1,1", "Cell 1,2"]
                    ]
                }
            ],
            "handwritten_items": [
                {"content": "Handwritten note"}
            ],
            "extracted_items": [
                {
                    "type": "paragraph",
                    "content": "Extracted paragraph"
                },
                {
                    "type": "table",
                    "content": [
                        ["Table Header 1", "Table Header 2"],
                        ["Table Cell 1,1", "Table Cell 1,2"]
                    ]
                }
            ]
        }
        
        # Call the method to test
        text = self.generator._extract_text_from_document(document_content)
        
        # Verify the result
        self.assertIn("Paragraph 1", text)
        self.assertIn("Paragraph 2", text)
        self.assertIn("Header 1 Header 2", text)
        self.assertIn("Cell 1,1 Cell 1,2", text)
        self.assertIn("Handwritten note", text)
        self.assertIn("Extracted paragraph", text)
        self.assertIn("Table Header 1 Table Header 2", text)
        self.assertIn("Table Cell 1,1 Table Cell 1,2", text)
    
    def test_split_into_sentences(self):
        """Test splitting text into sentences."""
        # Create test text
        text = "This is the first sentence. This is the second sentence! This is the third sentence? This is the fourth sentence."
        
        # Call the method to test
        sentences = self.generator._split_into_sentences(text)
        
        # Verify the result
        self.assertEqual(len(sentences), 4)
        self.assertEqual(sentences[0], "This is the first sentence")
        self.assertEqual(sentences[1], "This is the second sentence")
        self.assertEqual(sentences[2], "This is the third sentence")
        self.assertEqual(sentences[3], "This is the fourth sentence")
    
    def test_score_sentences(self):
        """Test scoring sentences."""
        # Create test sentences
        sentences = [
            "This is a sentence about important topics like document analysis.",
            "This is another sentence about document analysis.",
            "This sentence is not related to the main topic."
        ]
        
        # Call the method to test
        scores = self.generator._score_sentences(sentences)
        
        # Verify the result
        self.assertEqual(len(scores), 3)
        self.assertIn(sentences[0], scores)
        self.assertIn(sentences[1], scores)
        self.assertIn(sentences[2], scores)
        
        # Verify that sentences with common words have higher scores
        self.assertGreater(scores[sentences[0]], scores[sentences[2]])
        self.assertGreater(scores[sentences[1]], scores[sentences[2]])
    
    def test_calculate_word_frequencies(self):
        """Test calculating word frequencies."""
        # Create test sentences
        sentences = [
            "This is a document about document analysis.",
            "Document analysis is important for information extraction."
        ]
        
        # Call the method to test
        frequencies = self.generator._calculate_word_frequencies(sentences)
        
        # Verify the result
        self.assertIn("document", frequencies)
        self.assertIn("analysis", frequencies)
        
        # Verify that common words have higher frequencies
        self.assertEqual(frequencies["document"], 1.0)  # Normalized to 1.0 as the most frequent word
        self.assertEqual(frequencies["analysis"], 1.0)  # Also appears twice
    
    def test_tokenize(self):
        """Test tokenizing text."""
        # Create test text
        text = "This is a sample text with some stop words and important keywords like document analysis."
        
        # Call the method to test
        tokens = self.generator._tokenize(text)
        
        # Verify the result
        self.assertIn("sample", tokens)
        self.assertIn("text", tokens)
        self.assertIn("important", tokens)
        self.assertIn("keywords", tokens)
        self.assertIn("document", tokens)
        self.assertIn("analysis", tokens)
        
        # Verify that stop words are removed
        self.assertNotIn("this", tokens)
        self.assertNotIn("is", tokens)
        self.assertNotIn("a", tokens)
        self.assertNotIn("with", tokens)
        self.assertNotIn("some", tokens)
        self.assertNotIn("and", tokens)
        self.assertNotIn("like", tokens)
    
    def test_get_stop_words(self):
        """Test getting stop words."""
        # Call the method to test
        stop_words = self.generator._get_stop_words()
        
        # Verify the result
        self.assertIn("the", stop_words)
        self.assertIn("and", stop_words)
        self.assertIn("is", stop_words)
        self.assertIn("are", stop_words)
        self.assertIn("to", stop_words)
        self.assertIn("from", stop_words)
    
    def test_select_summary_sentences(self):
        """Test selecting summary sentences."""
        # Create test sentences and scores
        sentences = [
            "First sentence.",
            "Second sentence.",
            "Third sentence.",
            "Fourth sentence.",
            "Fifth sentence."
        ]
        scores = {
            "First sentence.": 0.5,
            "Second sentence.": 0.8,
            "Third sentence.": 0.3,
            "Fourth sentence.": 0.9,
            "Fifth sentence.": 0.7
        }
        
        # Call the method to test
        summary_sentences = self.generator._select_summary_sentences(sentences, scores)
        
        # Verify the result
        self.assertEqual(len(summary_sentences), 3)  # max_summary_length is 3
        self.assertIn("Fourth sentence.", summary_sentences)  # Highest score
        self.assertIn("Second sentence.", summary_sentences)  # Second highest score
        self.assertIn("Fifth sentence.", summary_sentences)   # Third highest score
        
        # Verify that sentences are in the original order
        self.assertEqual(summary_sentences.index("Second sentence."), 1)
        self.assertEqual(summary_sentences.index("Fourth sentence."), 3)
        self.assertEqual(summary_sentences.index("Fifth sentence."), 4)
    
    def test_extract_keywords(self):
        """Test extracting keywords."""
        # Create test text
        text = "This is a document about document analysis. Document analysis is important for information extraction. Keywords are useful for search and categorization."
        
        # Call the method to test
        keywords = self.generator._extract_keywords(text, num_keywords=5)
        
        # Verify the result
        self.assertEqual(len(keywords), 5)
        self.assertIn("document", keywords)
        self.assertIn("analysis", keywords)
        
        # Verify that the most frequent words are included
        self.assertEqual(keywords[0], "document")  # Most frequent word
        self.assertEqual(keywords[1], "analysis")  # Second most frequent word


class TestCreateSummaryGenerator(unittest.TestCase):
    """Tests for the create_summary_generator function."""
    
    def test_create_generator(self):
        """Test creating a SummaryGenerator."""
        # Call the function to test
        generator = create_summary_generator(max_summary_length=4)
        
        # Verify the result
        self.assertIsInstance(generator, SummaryGenerator)
        self.assertEqual(generator.max_summary_length, 4)


if __name__ == "__main__":
    unittest.main()
