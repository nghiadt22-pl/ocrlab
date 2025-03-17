"""
Image Extraction Module

This module provides functionality for extracting images from documents
using Azure Document Intelligence.
"""

import logging
import base64
from typing import Dict, Any, List, Optional

from .client import DocumentIntelligenceClient

# Configure logging
logger = logging.getLogger(__name__)


class ImageExtractor:
    """
    Class for extracting images from documents using Azure Document Intelligence.
    """
    
    def __init__(self, client: DocumentIntelligenceClient):
        """
        Initialize the ImageExtractor.
        
        Args:
            client: The Document Intelligence client to use for extraction.
        """
        self.client = client
        logger.info("ImageExtractor initialized")
    
    def extract_images(self, document_bytes: bytes) -> Dict[str, Any]:
        """
        Extract images from a document.
        
        Args:
            document_bytes: The document content as bytes.
        
        Returns:
            Dict[str, Any]: A dictionary containing the extracted images.
        """
        logger.info("Extracting images from document")
        
        # Analyze the document using the prebuilt-document model
        # This model is better for document understanding including images
        result = self.client.analyze_document(document_bytes, model_id="prebuilt-document")
        
        # Extract images
        images = self._extract_images(result)
        
        # Create the response
        response = {
            "images": images,
            "image_count": len(images)
        }
        
        logger.info(f"Extracted {len(images)} images from document")
        return response
    
    def _extract_images(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract images from the analysis result.
        
        Args:
            result: The document analysis result.
        
        Returns:
            List[Dict[str, Any]]: A list of images with their content and metadata.
        """
        images = []
        
        # Method 1: Extract from document content
        if "pages" in result.get("analyze_result", {}):
            for page_idx, page in enumerate(result["analyze_result"]["pages"]):
                # Check for images in the page
                if "images" in page:
                    for img_idx, image in enumerate(page["images"]):
                        image_obj = {
                            "id": f"image-page{page_idx}-{img_idx}",
                            "page_number": page.get("page_number", page_idx + 1),
                            "confidence": image.get("confidence", 0.9),
                            "bounding_box": self._extract_bounding_box(image),
                            "content": self._get_image_content(image),
                        }
                        images.append(image_obj)
        
        # Method 2: Extract from visual elements
        if "visual_elements" in result.get("analyze_result", {}):
            for ve_idx, visual_element in enumerate(result["analyze_result"]["visual_elements"]):
                if visual_element.get("kind", "") == "image":
                    image_obj = {
                        "id": f"image-visual-{ve_idx}",
                        "page_number": self._get_page_number(visual_element),
                        "confidence": visual_element.get("confidence", 0.9),
                        "bounding_box": self._extract_bounding_box(visual_element),
                        "content": self._get_image_content(visual_element),
                    }
                    images.append(image_obj)
        
        # Method 3: Extract from figures in the document
        if "figures" in result.get("analyze_result", {}):
            for fig_idx, figure in enumerate(result["analyze_result"]["figures"]):
                image_obj = {
                    "id": f"image-figure-{fig_idx}",
                    "page_number": self._get_page_number(figure),
                    "confidence": figure.get("confidence", 0.9),
                    "bounding_box": self._extract_bounding_box(figure),
                    "content": self._get_image_content(figure),
                }
                images.append(image_obj)
        
        # Deduplicate images based on bounding box overlap
        return self._deduplicate_images(images)
    
    def _get_image_content(self, image: Dict[str, Any]) -> str:
        """
        Get the image content.
        
        In a real implementation, this would extract the actual image data.
        For now, we return a placeholder or the image URL if available.
        
        Args:
            image: The image element from the analysis result.
        
        Returns:
            str: The image content as a data URL or placeholder.
        """
        # Check if the image has a URL
        if "url" in image:
            return image["url"]
        
        # Check if the image has binary data
        if "data" in image:
            try:
                # Convert binary data to base64
                base64_data = base64.b64encode(image["data"]).decode("utf-8")
                mime_type = image.get("mime_type", "image/png")
                return f"data:{mime_type};base64,{base64_data}"
            except Exception as e:
                logger.error(f"Error encoding image data: {str(e)}")
        
        # Return a placeholder
        return "https://placehold.co/600x400/png"
    
    def _deduplicate_images(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate images based on bounding box overlap.
        
        Args:
            images: The list of images to deduplicate.
        
        Returns:
            List[Dict[str, Any]]: The deduplicated list of images.
        """
        if not images:
            return []
        
        # Sort images by page number and then by area (largest first)
        sorted_images = sorted(
            images,
            key=lambda img: (
                img["page_number"],
                -(img["bounding_box"]["width"] * img["bounding_box"]["height"])
                if img.get("bounding_box") else 0
            )
        )
        
        # Group images by page
        images_by_page = {}
        for img in sorted_images:
            page = img["page_number"]
            if page not in images_by_page:
                images_by_page[page] = []
            images_by_page[page].append(img)
        
        # Deduplicate images on each page
        deduplicated = []
        for page, page_images in images_by_page.items():
            kept_images = []
            for img in page_images:
                # Skip if this image doesn't have a bounding box
                if not img.get("bounding_box"):
                    kept_images.append(img)
                    continue
                
                # Check if this image overlaps significantly with any kept image
                is_duplicate = False
                for kept in kept_images:
                    if not kept.get("bounding_box"):
                        continue
                    
                    # Calculate overlap
                    overlap = self._calculate_overlap(img["bounding_box"], kept["bounding_box"])
                    if overlap > 0.7:  # 70% overlap threshold
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    kept_images.append(img)
            
            deduplicated.extend(kept_images)
        
        return deduplicated
    
    def _calculate_overlap(self, box1: Dict[str, float], box2: Dict[str, float]) -> float:
        """
        Calculate the overlap ratio between two bounding boxes.
        
        Args:
            box1: The first bounding box.
            box2: The second bounding box.
        
        Returns:
            float: The overlap ratio (0-1).
        """
        # Calculate intersection
        x_left = max(box1["x"], box2["x"])
        y_top = max(box1["y"], box2["y"])
        x_right = min(box1["x"] + box1["width"], box2["x"] + box2["width"])
        y_bottom = min(box1["y"] + box1["height"], box2["y"] + box2["height"])
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate areas
        box1_area = box1["width"] * box1["height"]
        box2_area = box2["width"] * box2["height"]
        
        # Calculate overlap ratio (intersection over minimum area)
        min_area = min(box1_area, box2_area)
        if min_area == 0:
            return 0.0
        
        return intersection_area / min_area
    
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


# Factory function to create an ImageExtractor
def create_image_extractor(client: DocumentIntelligenceClient) -> ImageExtractor:
    """
    Create an ImageExtractor.
    
    Args:
        client: The Document Intelligence client to use for extraction.
    
    Returns:
        ImageExtractor: An ImageExtractor instance.
    """
    return ImageExtractor(client)
