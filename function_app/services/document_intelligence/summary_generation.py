"""
Summary Generation Module

This module provides functionality for generating summaries from document content
using natural language processing techniques.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
import math

# Configure logging
logger = logging.getLogger(__name__)


class SummaryGenerator:
    """
    Class for generating summaries from document content.
    
    This class uses extractive summarization techniques to identify
    the most important sentences in a document and create a concise summary.
    """
    
    def __init__(self, max_summary_length: int = 5):
        """
        Initialize the SummaryGenerator.
        
        Args:
            max_summary_length: The maximum number of sentences to include in the summary.
        """
        self.max_summary_length = max_summary_length
        logger.info("SummaryGenerator initialized")
    
    def generate_summary(self, document_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary from document content.
        
        Args:
            document_content: The document content, including paragraphs, tables, etc.
        
        Returns:
            Dict[str, Any]: A dictionary containing the generated summary.
        """
        logger.info("Generating summary from document content")
        
        # Extract text from paragraphs
        text = self._extract_text_from_document(document_content)
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            logger.warning("No sentences found in document")
            return {
                "summary": "",
                "keywords": [],
                "document_type": document_content.get("document_type", "unknown"),
                "language": document_content.get("language", "unknown"),
                "page_count": document_content.get("page_count", 0)
            }
        
        # Calculate sentence scores
        sentence_scores = self._score_sentences(sentences)
        
        # Select top sentences for summary
        summary_sentences = self._select_summary_sentences(sentences, sentence_scores)
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        # Create the summary
        summary = " ".join(summary_sentences)
        
        # Create the response
        response = {
            "summary": summary,
            "keywords": keywords,
            "document_type": document_content.get("document_type", "unknown"),
            "language": document_content.get("language", "unknown"),
            "page_count": document_content.get("page_count", 0)
        }
        
        logger.info(f"Generated summary with {len(summary_sentences)} sentences and {len(keywords)} keywords")
        return response
    
    def _extract_text_from_document(self, document_content: Dict[str, Any]) -> str:
        """
        Extract text from document content.
        
        Args:
            document_content: The document content, including paragraphs, tables, etc.
        
        Returns:
            str: The extracted text.
        """
        text_parts = []
        
        # Extract text from paragraphs
        if "paragraphs" in document_content:
            for paragraph in document_content["paragraphs"]:
                text_parts.append(paragraph.get("content", ""))
        
        # Extract text from tables
        if "tables" in document_content:
            for table in document_content["tables"]:
                if "rows" in table:
                    for row in table["rows"]:
                        text_parts.append(" ".join(row))
        
        # Extract text from handwritten items
        if "handwritten_items" in document_content:
            for item in document_content["handwritten_items"]:
                text_parts.append(item.get("content", ""))
        
        # Extract text from extracted_items
        if "extracted_items" in document_content:
            for item in document_content["extracted_items"]:
                if item.get("type") == "paragraph":
                    text_parts.append(item.get("content", ""))
                elif item.get("type") == "table":
                    if isinstance(item.get("content"), list):
                        for row in item.get("content", []):
                            if isinstance(row, list):
                                text_parts.append(" ".join(row))
        
        # Join all text parts
        return " ".join(text_parts)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: The text to split.
        
        Returns:
            List[str]: A list of sentences.
        """
        # Simple sentence splitting using regex
        # This is a basic implementation and could be improved with NLP libraries
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        
        # Filter out empty sentences, normalize whitespace, and remove trailing punctuation
        sentences = [re.sub(r'[.!?]$', '', s.strip()) for s in sentences if s.strip()]
        
        return sentences
    
    def _score_sentences(self, sentences: List[str]) -> Dict[str, float]:
        """
        Score sentences based on their importance.
        
        Args:
            sentences: The list of sentences to score.
        
        Returns:
            Dict[str, float]: A dictionary mapping sentences to their scores.
        """
        # Calculate word frequencies
        word_frequencies = self._calculate_word_frequencies(sentences)
        
        # Calculate sentence scores
        sentence_scores = {}
        for sentence in sentences:
            words = self._tokenize(sentence)
            score = sum(word_frequencies.get(word.lower(), 0) for word in words)
            
            # Normalize by sentence length to avoid bias towards longer sentences
            if len(words) > 0:
                score = score / len(words)
            
            sentence_scores[sentence] = score
        
        return sentence_scores
    
    def _calculate_word_frequencies(self, sentences: List[str]) -> Dict[str, float]:
        """
        Calculate word frequencies in the document.
        
        Args:
            sentences: The list of sentences in the document.
        
        Returns:
            Dict[str, float]: A dictionary mapping words to their frequencies.
        """
        # Tokenize all sentences
        all_words = []
        for sentence in sentences:
            words = self._tokenize(sentence)
            all_words.extend(words)
        
        # Calculate word frequencies
        word_frequencies = {}
        for word in all_words:
            word = word.lower()
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
        
        # Group words by frequency
        frequency_groups = {}
        for word, freq in word_frequencies.items():
            if freq not in frequency_groups:
                frequency_groups[freq] = []
            frequency_groups[freq].append(word)
        
        # Normalize word frequencies
        max_frequency = max(word_frequencies.values()) if word_frequencies else 1
        for word in word_frequencies:
            word_frequencies[word] = round(word_frequencies[word] / max_frequency, 2)
        
        return word_frequencies
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: The text to tokenize.
        
        Returns:
            List[str]: A list of words.
        """
        # Simple tokenization using regex
        # This is a basic implementation and could be improved with NLP libraries
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words
        stop_words = self._get_stop_words()
        words = [word for word in words if word not in stop_words]
        
        return words
    
    def _get_stop_words(self) -> List[str]:
        """
        Get a list of stop words.
        
        Returns:
            List[str]: A list of stop words.
        """
        # Basic list of English stop words
        # This could be expanded or replaced with a more comprehensive list
        return [
            "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
            "which", "this", "that", "these", "those", "then", "just", "so", "than",
            "such", "when", "who", "how", "where", "why", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "having", "do", "does", "did",
            "doing", "to", "from", "in", "out", "on", "off", "over", "under", "again",
            "further", "then", "once", "here", "there", "all", "any", "both", "each",
            "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
            "own", "same", "so", "than", "too", "very", "can", "will", "should", "now",
            "with", "some", "for", "at", "by", "about", "against", "between", "into",
            "through", "during", "before", "after", "above", "below", "up", "down",
            "of", "my", "me", "mine", "your", "yours", "his", "her", "hers", "its",
            "our", "ours", "their", "theirs", "am", "i", "you", "he", "she", "it",
            "we", "they", "them", "us", "him", "himself", "herself", "itself",
            "ourselves", "themselves", "myself", "yourself", "yourselves"
        ]
    
    def _select_summary_sentences(
        self, sentences: List[str], sentence_scores: Dict[str, float]
    ) -> List[str]:
        """
        Select the top sentences for the summary.
        
        Args:
            sentences: The list of sentences in the document.
            sentence_scores: The scores for each sentence.
        
        Returns:
            List[str]: The selected sentences for the summary.
        """
        # Sort sentences by score
        sorted_sentences = sorted(
            sentence_scores.items(), key=lambda x: x[1], reverse=True
        )
        
        # Select top sentences
        top_sentences = [sentence for sentence, score in sorted_sentences[:self.max_summary_length]]
        
        # Return sentences in their original order from the input list
        return [sentence for sentence in sentences if sentence in top_sentences]
    
    def _extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: The text to extract keywords from.
            num_keywords: The number of keywords to extract.
        
        Returns:
            List[str]: A list of keywords.
        """
        # Tokenize text
        words = self._tokenize(text)
        
        # Calculate word frequencies
        word_frequencies = {}
        for word in words:
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
        
        # Sort words by frequency
        sorted_words = sorted(
            word_frequencies.items(), key=lambda x: x[1], reverse=True
        )
        
        # Select top keywords
        keywords = [word for word, freq in sorted_words[:num_keywords]]
        
        return keywords


# Factory function to create a SummaryGenerator
def create_summary_generator(max_summary_length: int = 5) -> SummaryGenerator:
    """
    Create a SummaryGenerator.
    
    Args:
        max_summary_length: The maximum number of sentences to include in the summary.
    
    Returns:
        SummaryGenerator: A SummaryGenerator instance.
    """
    return SummaryGenerator(max_summary_length)
