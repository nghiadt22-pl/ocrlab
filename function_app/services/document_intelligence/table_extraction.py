"""
Table Extraction Module

This module provides functionality for extracting tables from documents
using Azure Document Intelligence.
"""

import logging
from typing import Dict, Any, List, Optional

from .client import DocumentIntelligenceClient

# Configure logging
logger = logging.getLogger(__name__)


class TableExtractor:
    """
    Class for extracting tables from documents using Azure Document Intelligence.
    """
    
    def __init__(self, client: DocumentIntelligenceClient):
        """
        Initialize the TableExtractor.
        
        Args:
            client: The Document Intelligence client to use for extraction.
        """
        self.client = client
        logger.info("TableExtractor initialized")
    
    def extract_tables(self, document_bytes: bytes) -> Dict[str, Any]:
        """
        Extract tables from a document.
        
        Args:
            document_bytes: The document content as bytes.
        
        Returns:
            Dict[str, Any]: A dictionary containing the extracted tables.
        """
        logger.info("Extracting tables from document")
        
        # Analyze the document using the prebuilt-layout model
        # This model is good for general layout analysis including tables
        result = self.client.analyze_document(document_bytes, model_id="prebuilt-layout")
        
        # Extract tables
        tables = self._extract_tables(result)
        
        # Create the response
        response = {
            "tables": tables,
            "table_count": len(tables)
        }
        
        logger.info(f"Extracted {len(tables)} tables from document")
        return response
    
    def _extract_tables(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tables from the analysis result.
        
        Args:
            result: The document analysis result.
        
        Returns:
            List[Dict[str, Any]]: A list of tables with their content and metadata.
        """
        tables = []
        
        if "tables" in result.get("analyze_result", {}):
            for idx, table in enumerate(result["analyze_result"]["tables"]):
                # Get the cells organized by row and column
                rows = self._organize_table_cells(table)
                
                # Create the table object
                table_obj = {
                    "id": f"table-{idx}",
                    "rows": rows,
                    "row_count": table.get("row_count", len(rows)),
                    "column_count": table.get("column_count", len(rows[0]) if rows else 0),
                    "confidence": table.get("confidence", 0.0),
                    "page_number": self._get_page_number(table),
                    "bounding_box": self._extract_bounding_box(table)
                }
                
                tables.append(table_obj)
        
        return tables
    
    def _organize_table_cells(self, table: Dict[str, Any]) -> List[List[str]]:
        """
        Organize table cells into a 2D array.
        
        Args:
            table: The table from the analysis result.
        
        Returns:
            List[List[str]]: A 2D array of cell contents.
        """
        if "cells" not in table:
            return []
        
        # Determine table dimensions
        row_count = max([cell.get("row_index", 0) for cell in table["cells"]]) + 1
        column_count = max([cell.get("column_index", 0) for cell in table["cells"]]) + 1
        
        # Initialize the 2D array with empty strings
        rows = []
        for _ in range(row_count):
            rows.append([""] * column_count)
        
        # Fill in the table cells
        for cell in table["cells"]:
            row_index = cell.get("row_index", 0)
            column_index = cell.get("column_index", 0)
            content = cell.get("content", "")
            
            # Handle row and column spans
            row_span = cell.get("row_span", 1)
            column_span = cell.get("column_span", 1)
            
            # Fill in the cell and any spanned cells
            for r in range(row_index, min(row_index + row_span, row_count)):
                for c in range(column_index, min(column_index + column_span, column_count)):
                    rows[r][c] = content
        
        return rows
    
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


# Factory function to create a TableExtractor
def create_table_extractor(client: DocumentIntelligenceClient) -> TableExtractor:
    """
    Create a TableExtractor.
    
    Args:
        client: The Document Intelligence client to use for extraction.
    
    Returns:
        TableExtractor: A TableExtractor instance.
    """
    return TableExtractor(client)
