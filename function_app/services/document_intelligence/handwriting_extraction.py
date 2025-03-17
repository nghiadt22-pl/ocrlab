"""
Handwriting Extraction Module

This module provides functionality for extracting handwritten text from documents
using Azure Document Intelligence.
"""

import logging
from typing import Dict, Any, List, Optional

from .client import DocumentIntelligenceClient

# Configure logging
logger = logging.getLogger(__name__)


class HandwritingExtractor:
    """
    Class for extracting handwritten text from documents using Azure Document Intelligence.
    """
    
    def __init__(self, client: DocumentIntelligenceClient):
        """
        Initialize the HandwritingExtractor.
        
        Args:
            client: The Document Intelligence client to use for extraction.
        """
        self.client = client
        logger.info("HandwritingExtractor initialized")
    
    def extract_handwriting(self, document_bytes: bytes) -> Dict[str, Any]:
        """
        Extract handwritten text from a document.
        
        Args:
            document_bytes: The document content as bytes.
        
        Returns:
            Dict[str, Any]: A dictionary containing the extracted handwritten text.
        """
        logger.info("Extracting handwritten text from document")
        
        # Analyze the document using the prebuilt-read model
        # This model is optimized for text reading including handwriting
        result = self.client.analyze_document(document_bytes, model_id="prebuilt-read")
        
        # Extract handwritten text
        handwritten_items = self._extract_handwritten_items(result)
        
        # Create the response
        response = {
            "handwritten_items": handwritten_items,
            "handwriting_count": len(handwritten_items)
        }
        
        logger.info(f"Extracted {len(handwritten_items)} handwritten items from document")
        return response
    
    def _extract_handwritten_items(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract handwritten items from the analysis result.
        
        Args:
            result: The document analysis result.
        
        Returns:
            List[Dict[str, Any]]: A list of handwritten items with their content and metadata.
        """
        handwritten_items = []
        
        # Method 1: Extract from styles
        if "styles" in result.get("analyze_result", {}):
            # Get all spans with handwritten style
            handwritten_spans = []
            for style in result["analyze_result"]["styles"]:
                if style.get("is_handwritten", False) and style.get("confidence", 0) > 0.5:
                    handwritten_spans.append({
                        "span": style.get("span", {}),
                        "confidence": style.get("confidence", 0.0),
                        "page_number": self._get_page_number_from_style(style)
                    })
            
            # Match spans with content
            if handwritten_spans and "spans" in result.get("analyze_result", {}):
                for idx, hw_span in enumerate(handwritten_spans):
                    span_offset = hw_span["span"].get("offset", 0)
                    span_length = hw_span["span"].get("length", 0)
                    
                    # Find the content for this span
                    content = self._find_content_for_span(
                        result["analyze_result"]["spans"],
                        span_offset,
                        span_length
                    )
                    
                    if content:
                        handwritten_item = {
                            "id": f"handwriting-{idx}",
                            "content": content,
                            "confidence": hw_span["confidence"],
                            "page_number": hw_span["page_number"],
                            "bounding_box": self._find_bounding_box_for_span(
                                result, span_offset, span_length
                            )
                        }
                        handwritten_items.append(handwritten_item)
        
        # Method 2: Extract from lines with handwritten style
        if "pages" in result.get("analyze_result", {}):
            for page_idx, page in enumerate(result["analyze_result"]["pages"]):
                page_number = page.get("page_number", page_idx + 1)
                
                # Check for lines in the page
                if "lines" in page:
                    for line_idx, line in enumerate(page["lines"]):
                        # Check if this line is marked as handwritten
                        if line.get("is_handwritten", False) or "handwritten" in line.get("appearance", "").lower():
                            handwritten_item = {
                                "id": f"handwriting-page{page_number}-line{line_idx}",
                                "content": line.get("content", ""),
                                "confidence": line.get("confidence", 0.7),
                                "page_number": page_number,
                                "bounding_box": self._extract_bounding_box(line)
                            }
                            handwritten_items.append(handwritten_item)
        
        # Method 3: Extract from words with handwritten style
        if "pages" in result.get("analyze_result", {}):
            for page_idx, page in enumerate(result["analyze_result"]["pages"]):
                page_number = page.get("page_number", page_idx + 1)
                
                # Check for words in the page
                if "words" in page:
                    handwritten_words = []
                    for word_idx, word in enumerate(page["words"]):
                        # Check if this word is marked as handwritten
                        if word.get("is_handwritten", False) or "handwritten" in word.get("appearance", "").lower():
                            handwritten_item = {
                                "id": f"handwriting-page{page_number}-word{word_idx}",
                                "content": word.get("content", ""),
                                "confidence": word.get("confidence", 0.7),
                                "page_number": page_number,
                                "bounding_box": self._extract_bounding_box(word)
                            }
                            handwritten_items.append(handwritten_item)
        
        # Deduplicate and merge handwritten items
        return self._merge_handwritten_items(handwritten_items)
    
    def _find_content_for_span(
        self, spans: List[Dict[str, Any]], offset: int, length: int
    ) -> Optional[str]:
        """
        Find the content for a span based on offset and length.
        
        Args:
            spans: The list of spans from the analysis result.
            offset: The offset of the span.
            length: The length of the span.
        
        Returns:
            Optional[str]: The content of the span, or None if not found.
        """
        for span in spans:
            if span.get("offset") == offset and span.get("length") == length:
                return span.get("content", "")
        return None
    
    def _find_bounding_box_for_span(
        self, result: Dict[str, Any], offset: int, length: int
    ) -> Optional[Dict[str, float]]:
        """
        Find the bounding box for a span based on offset and length.
        
        Args:
            result: The document analysis result.
            offset: The offset of the span.
            length: The length of the span.
        
        Returns:
            Optional[Dict[str, float]]: The bounding box of the span, or None if not found.
        """
        # Check in lines
        if "pages" in result.get("analyze_result", {}):
            for page in result["analyze_result"]["pages"]:
                if "lines" in page:
                    for line in page["lines"]:
                        if line.get("span", {}).get("offset") == offset and line.get("span", {}).get("length") == length:
                            return self._extract_bounding_box(line)
                
                if "words" in page:
                    for word in page["words"]:
                        if word.get("span", {}).get("offset") == offset and word.get("span", {}).get("length") == length:
                            return self._extract_bounding_box(word)
        
        return None
    
    def _get_page_number_from_style(self, style: Dict[str, Any]) -> int:
        """
        Get the page number from a style element.
        
        Args:
            style: The style element.
        
        Returns:
            int: The page number.
        """
        if "bounding_regions" in style and style["bounding_regions"]:
            return style["bounding_regions"][0].get("page_number", 1)
        return 1
    
    def _merge_handwritten_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge and deduplicate handwritten items.
        
        Args:
            items: The list of handwritten items.
        
        Returns:
            List[Dict[str, Any]]: The merged and deduplicated list of handwritten items.
        """
        if not items:
            return []
        
        # Group items by page
        items_by_page = {}
        for item in items:
            page = item["page_number"]
            if page not in items_by_page:
                items_by_page[page] = []
            items_by_page[page].append(item)
        
        # Process each page
        merged_items = []
        for page, page_items in items_by_page.items():
            # Sort by y-coordinate (top to bottom)
            if all(item.get("bounding_box") for item in page_items):
                page_items.sort(key=lambda item: item["bounding_box"]["y"])
            
            # Merge items that are close to each other vertically
            current_group = []
            for item in page_items:
                if not current_group:
                    current_group.append(item)
                    continue
                
                # Check if this item is close to the current group
                if (self._are_items_close(current_group[-1], item) and 
                    len(current_group) < 5):  # Limit group size
                    current_group.append(item)
                else:
                    # Create a merged item from the current group
                    merged_item = self._create_merged_item(current_group)
                    merged_items.append(merged_item)
                    current_group = [item]
            
            # Don't forget the last group
            if current_group:
                merged_item = self._create_merged_item(current_group)
                merged_items.append(merged_item)
        
        return merged_items
    
    def _are_items_close(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """
        Check if two items are close to each other vertically.
        
        Args:
            item1: The first item.
            item2: The second item.
        
        Returns:
            bool: True if the items are close, False otherwise.
        """
        # If either item doesn't have a bounding box, assume they're not close
        if not item1.get("bounding_box") or not item2.get("bounding_box"):
            return False
        
        box1 = item1["bounding_box"]
        box2 = item2["bounding_box"]
        
        # Check vertical proximity
        box1_bottom = box1["y"] + box1["height"]
        vertical_distance = box2["y"] - box1_bottom
        
        # Items are close if the vertical distance is less than the height of the first item
        return vertical_distance < box1["height"]
    
    def _create_merged_item(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a merged item from a group of items.
        
        Args:
            items: The group of items to merge.
        
        Returns:
            Dict[str, Any]: The merged item.
        """
        if len(items) == 1:
            # For single items, add the merged_count key
            merged_item = items[0].copy()
            merged_item["merged_count"] = 1
            return merged_item
        
        # Merge content
        content = " ".join([item["content"] for item in items])
        
        # Calculate average confidence and round to 2 decimal places to avoid floating-point precision issues
        confidence = round(sum([item["confidence"] for item in items]) / len(items), 2)
        
        # Create a bounding box that encompasses all items
        bounding_box = None
        if all(item.get("bounding_box") for item in items):
            boxes = [item["bounding_box"] for item in items]
            x = min([box["x"] for box in boxes])
            y = min([box["y"] for box in boxes])
            max_x = max([box["x"] + box["width"] for box in boxes])
            max_y = max([box["y"] + box["height"] for box in boxes])
            
            bounding_box = {
                "x": x,
                "y": y,
                "width": max_x - x,
                "height": max_y - y
            }
        
        # Create the merged item
        return {
            "id": f"handwriting-merged-{items[0]['id']}",
            "content": content,
            "confidence": confidence,
            "page_number": items[0]["page_number"],
            "bounding_box": bounding_box,
            "merged_count": len(items)
        }
    
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
        
        # Alternative: check for bounding_box directly
        if "bounding_box" in element:
            return element["bounding_box"]
        
        return None


# Factory function to create a HandwritingExtractor
def create_handwriting_extractor(client: DocumentIntelligenceClient) -> HandwritingExtractor:
    """
    Create a HandwritingExtractor.
    
    Args:
        client: The Document Intelligence client to use for extraction.
    
    Returns:
        HandwritingExtractor: A HandwritingExtractor instance.
    """
    return HandwritingExtractor(client)
