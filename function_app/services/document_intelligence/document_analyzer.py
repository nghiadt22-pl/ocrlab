"""
Document Analyzer Module

This module provides a comprehensive document analyzer that combines
text, table, image, and handwriting extraction capabilities.
"""

import logging
from typing import Dict, Any, List, Optional, BinaryIO

from .client import DocumentIntelligenceClient, create_document_intelligence_client
from .text_extraction import TextExtractor, create_text_extractor
from .table_extraction import TableExtractor, create_table_extractor
from .image_extraction import ImageExtractor, create_image_extractor
from .handwriting_extraction import HandwritingExtractor, create_handwriting_extractor
from .summary_generation import SummaryGenerator, create_summary_generator

# Configure logging
logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """
    Class for comprehensive document analysis using Azure Document Intelligence.
    
    This class combines text, table, image, and handwriting extraction capabilities
    to provide a complete analysis of documents.
    """
    
    def __init__(
        self,
        client: Optional[DocumentIntelligenceClient] = None,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the DocumentAnalyzer.
        
        Args:
            client: The Document Intelligence client to use for analysis.
                   If not provided, a new client will be created.
            endpoint: The Azure Document Intelligence endpoint URL.
                      Used only if client is not provided.
            api_key: The Azure Document Intelligence API key.
                     Used only if client is not provided.
        """
        # Create or use the provided client
        self.client = client or create_document_intelligence_client(endpoint, api_key)
        
        # Initialize extractors
        self.text_extractor = create_text_extractor(self.client)
        self.table_extractor = create_table_extractor(self.client)
        self.image_extractor = create_image_extractor(self.client)
        self.handwriting_extractor = create_handwriting_extractor(self.client)
        self.summary_generator = create_summary_generator()
        
        logger.info("DocumentAnalyzer initialized")
    
    def analyze_document(
        self,
        document: BinaryIO,
        extract_text: bool = True,
        extract_tables: bool = True,
        extract_images: bool = True,
        extract_handwriting: bool = True,
        generate_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a document comprehensively.
        
        Args:
            document: The document file object.
            extract_text: Whether to extract text.
            extract_tables: Whether to extract tables.
            extract_images: Whether to extract images.
            extract_handwriting: Whether to extract handwriting.
        
        Returns:
            Dict[str, Any]: A dictionary containing the analysis results.
        """
        logger.info("Starting comprehensive document analysis")
        
        # Read the document bytes
        document_bytes = document.read()
        
        # Initialize the result dictionary
        result = {
            "document_type": "unknown",
            "language": "unknown",
            "page_count": 0
        }
        
        # Extract text if requested
        if extract_text:
            logger.info("Extracting text")
            text_result = self.text_extractor.extract_text(document_bytes)
            result.update({
                "paragraphs": text_result.get("paragraphs", []),
                "pages": text_result.get("pages", []),
                "document_type": text_result.get("document_type", "unknown"),
                "language": text_result.get("language", "unknown"),
                "page_count": text_result.get("page_count", 0)
            })
        
        # Extract tables if requested
        if extract_tables:
            logger.info("Extracting tables")
            table_result = self.table_extractor.extract_tables(document_bytes)
            result["tables"] = table_result.get("tables", [])
        
        # Extract images if requested
        if extract_images:
            logger.info("Extracting images")
            image_result = self.image_extractor.extract_images(document_bytes)
            result["images"] = image_result.get("images", [])
        
        # Extract handwriting if requested
        if extract_handwriting:
            logger.info("Extracting handwriting")
            handwriting_result = self.handwriting_extractor.extract_handwriting(document_bytes)
            result["handwritten_items"] = handwriting_result.get("handwritten_items", [])
        
        # Create a unified list of all extracted items
        extracted_items = self._create_unified_item_list(result)
        result["extracted_items"] = extracted_items
        
        # Generate summary if requested
        if generate_summary:
            logger.info("Generating document summary")
            summary_result = self.summary_generator.generate_summary(result)
            result["summary"] = summary_result.get("summary", "")
            result["keywords"] = summary_result.get("keywords", [])
        
        logger.info("Document analysis completed")
        return result
    
    def _create_unified_item_list(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a unified list of all extracted items.
        
        Args:
            result: The analysis result.
        
        Returns:
            List[Dict[str, Any]]: A unified list of all extracted items.
        """
        items = []
        
        # Add paragraphs
        if "paragraphs" in result:
            for para in result["paragraphs"]:
                items.append({
                    "id": para.get("id", f"paragraph-{len(items)}"),
                    "type": "paragraph",
                    "content": para.get("content", ""),
                    "confidence": para.get("confidence", 0.0),
                    "page_number": para.get("page_number", 1),
                    "bounding_box": para.get("bounding_box")
                })
        
        # Add tables
        if "tables" in result:
            for table in result["tables"]:
                items.append({
                    "id": table.get("id", f"table-{len(items)}"),
                    "type": "table",
                    "content": table.get("rows", []),
                    "confidence": table.get("confidence", 0.0),
                    "page_number": table.get("page_number", 1),
                    "bounding_box": table.get("bounding_box"),
                    "row_count": table.get("row_count", 0),
                    "column_count": table.get("column_count", 0)
                })
        
        # Add images
        if "images" in result:
            for image in result["images"]:
                items.append({
                    "id": image.get("id", f"image-{len(items)}"),
                    "type": "figure",
                    "content": image.get("content", ""),
                    "confidence": image.get("confidence", 0.0),
                    "page_number": image.get("page_number", 1),
                    "bounding_box": image.get("bounding_box")
                })
        
        # Add handwritten items
        if "handwritten_items" in result:
            for hw_item in result["handwritten_items"]:
                items.append({
                    "id": hw_item.get("id", f"handwriting-{len(items)}"),
                    "type": "handwriting",
                    "content": hw_item.get("content", ""),
                    "confidence": hw_item.get("confidence", 0.0),
                    "page_number": hw_item.get("page_number", 1),
                    "bounding_box": hw_item.get("bounding_box"),
                    "merged_count": hw_item.get("merged_count", 1)
                })
        
        # Sort items by page number and then by y-coordinate
        items.sort(key=lambda item: (
            item["page_number"],
            item["bounding_box"]["y"] if item.get("bounding_box") else float('inf')
        ))
        
        return items


# Factory function to create a DocumentAnalyzer
def create_document_analyzer(
    client: Optional[DocumentIntelligenceClient] = None,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None
) -> DocumentAnalyzer:
    """
    Create a DocumentAnalyzer.
    
    Args:
        client: The Document Intelligence client to use for analysis.
               If not provided, a new client will be created.
        endpoint: The Azure Document Intelligence endpoint URL.
                  Used only if client is not provided.
        api_key: The Azure Document Intelligence API key.
                 Used only if client is not provided.
    
    Returns:
        DocumentAnalyzer: A DocumentAnalyzer instance.
    """
    return DocumentAnalyzer(client, endpoint, api_key)
