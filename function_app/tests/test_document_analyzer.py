"""
Test script for the Document Analyzer

This script tests the document analyzer with a sample PDF file.
"""

import os
import sys
import logging
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the services
sys.path.append(str(Path(__file__).parent.parent))

# Print environment variables for debugging
print("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT:", os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"))
print("AZURE_DOCUMENT_INTELLIGENCE_KEY is set:", os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY") is not None)

from services.document_intelligence import create_document_analyzer


def test_document_analyzer():
    """Test the document analyzer with a sample PDF file."""
    # Get the path to the test PDF file
    test_pdf_path = os.path.join(os.path.dirname(__file__), "..", "test.pdf")
    if not os.path.exists(test_pdf_path):
        logger.error(f"Test PDF file not found at {test_pdf_path}")
        return False
    
    logger.info(f"Testing document analyzer with {test_pdf_path}")
    
    try:
        # Create a document analyzer
        document_analyzer = create_document_analyzer()
        
        # Open the PDF file
        with open(test_pdf_path, "rb") as pdf_file:
            # Analyze the document
            result = document_analyzer.analyze_document(
                document=pdf_file,
                extract_text=True,
                extract_tables=True,
                extract_images=True,
                extract_handwriting=True
            )
        
        # Log the results
        logger.info("Document analysis completed successfully")
        logger.info(f"Document type: {result.get('document_type', 'unknown')}")
        logger.info(f"Language: {result.get('language', 'unknown')}")
        logger.info(f"Page count: {result.get('page_count', 0)}")
        logger.info(f"Paragraphs: {len(result.get('paragraphs', []))}")
        logger.info(f"Tables: {len(result.get('tables', []))}")
        logger.info(f"Images: {len(result.get('images', []))}")
        logger.info(f"Handwritten items: {len(result.get('handwritten_items', []))}")
        logger.info(f"Total extracted items: {len(result.get('extracted_items', []))}")
        
        # Save the results to a JSON file for inspection
        output_path = os.path.join(os.path.dirname(__file__), "document_analyzer_result.json")
        
        # Create a simplified version of the result for JSON serialization
        simplified_result = {
            "document_type": result.get("document_type", "unknown"),
            "language": result.get("language", "unknown"),
            "page_count": result.get("page_count", 0),
            "paragraph_count": len(result.get("paragraphs", [])),
            "table_count": len(result.get("tables", [])),
            "image_count": len(result.get("images", [])),
            "handwriting_count": len(result.get("handwritten_items", [])),
            "extracted_item_count": len(result.get("extracted_items", [])),
            "extracted_items": [
                {
                    "id": item.get("id", ""),
                    "type": item.get("type", "unknown"),
                    "page_number": item.get("page_number", 1),
                    "confidence": item.get("confidence", 0.0),
                    # Include a preview of the content
                    "content_preview": str(item.get("content", ""))[:100] + "..." if item.get("content") else ""
                }
                for item in result.get("extracted_items", [])
            ]
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(simplified_result, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error testing document analyzer: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = test_document_analyzer()
    sys.exit(0 if success else 1)
