"""
Text Extraction Module

This module provides functionality for extracting text from PDF documents
using Azure Document Intelligence.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from .client import DocumentIntelligenceClient

# Configure logging
logger = logging.getLogger(__name__)


class TextExtractor:
    """
    Class for extracting text from documents using Azure Document Intelligence.
    """
    
    def __init__(self, client: DocumentIntelligenceClient):
        """
        Initialize the TextExtractor.
        
        Args:
            client: The Document Intelligence client to use for extraction.
        """
        self.client = client
        logger.info("TextExtractor initialized")
    
    def extract_text(self, document_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from a document.
        
        Args:
            document_bytes: The document content as bytes.
        
        Returns:
            Dict[str, Any]: A dictionary containing the extracted text content.
        """
        logger.info("Extracting text from document")
        
        # Analyze the document using the prebuilt-layout model
        result = self.client.analyze_document(document_bytes, model_id="prebuilt-layout")
        
        # Extract paragraphs
        paragraphs = self._extract_paragraphs(result)
        
        # Extract content by page
        pages_content = self._extract_content_by_page(result)
        
        # Create the response
        response = {
            "paragraphs": paragraphs,
            "pages": pages_content,
            "document_type": self._determine_document_type(result),
            "language": self._extract_language(result),
            "page_count": self._get_page_count(result)
        }
        
        logger.info(f"Extracted {len(paragraphs)} paragraphs from {response['page_count']} pages")
        return response
    
    def _extract_paragraphs(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract paragraphs from the analysis result.
        
        Args:
            result: The document analysis result.
        
        Returns:
            List[Dict[str, Any]]: A list of paragraphs with their content and metadata.
        """
        paragraphs = []
        
        if "paragraphs" in result.get("analyze_result", {}):
            for idx, para in enumerate(result["analyze_result"]["paragraphs"]):
                paragraph = {
                    "id": f"paragraph-{idx}",
                    "content": para.get("content", ""),
                    "confidence": para.get("confidence", 0.0),
                    "page_number": self._get_page_number(para),
                    "bounding_box": self._extract_bounding_box(para)
                }
                paragraphs.append(paragraph)
        
        return paragraphs
    
    def _extract_content_by_page(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract content organized by page.
        
        Args:
            result: The document analysis result.
        
        Returns:
            List[Dict[str, Any]]: A list of pages with their content.
        """
        pages = []
        
        if "pages" in result.get("analyze_result", {}):
            for page in result["analyze_result"]["pages"]:
                page_number = page.get("page_number", 0)
                
                # Get paragraphs for this page
                page_paragraphs = []
                if "paragraphs" in result.get("analyze_result", {}):
                    for idx, para in enumerate(result["analyze_result"]["paragraphs"]):
                        if self._get_page_number(para) == page_number:
                            page_paragraphs.append({
                                "id": f"paragraph-{idx}",
                                "content": para.get("content", ""),
                                "confidence": para.get("confidence", 0.0),
                                "bounding_box": self._extract_bounding_box(para)
                            })
                
                # Create the page object
                page_obj = {
                    "page_number": page_number,
                    "width": page.get("width", 0),
                    "height": page.get("height", 0),
                    "unit": page.get("unit", "pixel"),
                    "paragraphs": page_paragraphs,
                    "text": self._get_page_text(page_paragraphs)
                }
                
                pages.append(page_obj)
        
        # Sort pages by page number
        pages.sort(key=lambda x: x["page_number"])
        
        return pages
    
    def _get_page_text(self, paragraphs: List[Dict[str, Any]]) -> str:
        """
        Get the full text of a page by concatenating all paragraphs.
        
        Args:
            paragraphs: The paragraphs on the page.
        
        Returns:
            str: The full text of the page.
        """
        return "\n".join([p["content"] for p in paragraphs])
    
    def _get_page_number(self, element: Dict[str, Any]) -> int:
        """
        Get the page number from an element.
        
        Args:
            element: The element to get the page number from.
        
        Returns:
            int: The page number.
        """
        if "bounding_regions" in element and element["bounding_regions"]:
            return element["bounding_regions"][0].get("page_number", 1)
        return 1
    
    def _extract_bounding_box(self, element: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """
        Extract the bounding box from an element.
        
        Args:
            element: The element to extract the bounding box from.
        
        Returns:
            Optional[Dict[str, float]]: The bounding box coordinates, or None if not available.
        """
        if "bounding_regions" in element and element["bounding_regions"]:
            region = element["bounding_regions"][0]
            if "polygon" in region and len(region["polygon"]) >= 8:
                polygon = region["polygon"]
                # Convert polygon to bounding box (x, y, width, height)
                x = min(polygon[0], polygon[2], polygon[4], polygon[6])
                y = min(polygon[1], polygon[3], polygon[5], polygon[7])
                width = max(polygon[0], polygon[2], polygon[4], polygon[6]) - x
                height = max(polygon[1], polygon[3], polygon[5], polygon[7]) - y
                
                return {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                }
        
        return None
    
    def _determine_document_type(self, result: Dict[str, Any]) -> str:
        """
        Determine the document type based on the analysis result.
        
        Args:
            result: The document analysis result.
        
        Returns:
            str: The document type.
        """
        # This is a simplified implementation
        # In a real-world scenario, you might use more sophisticated logic
        if "documents" in result.get("analyze_result", {}):
            doc_types = [doc.get("doc_type", "") for doc in result["analyze_result"]["documents"]]
            if doc_types:
                return doc_types[0]
        
        return "general"
    
    def _extract_language(self, result: Dict[str, Any]) -> str:
        """
        Extract the language from the analysis result.
        
        Args:
            result: The document analysis result.
        
        Returns:
            str: The detected language.
        """
        # Check if language is available in the result
        if "languages" in result.get("analyze_result", {}):
            languages = result["analyze_result"]["languages"]
            if languages:
                return languages[0].get("locale", "en")
        
        return "en"  # Default to English
    
    def _get_page_count(self, result: Dict[str, Any]) -> int:
        """
        Get the number of pages in the document.
        
        Args:
            result: The document analysis result.
        
        Returns:
            int: The number of pages.
        """
        if "pages" in result.get("analyze_result", {}):
            return len(result["analyze_result"]["pages"])
        return 0


# Factory function to create a TextExtractor
def create_text_extractor(client: DocumentIntelligenceClient) -> TextExtractor:
    """
    Create a TextExtractor.
    
    Args:
        client: The Document Intelligence client to use for extraction.
    
    Returns:
        TextExtractor: A TextExtractor instance.
    """
    return TextExtractor(client) 