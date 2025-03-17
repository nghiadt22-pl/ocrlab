"""
Test script for imports

This script tests if we can import the modules correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Add the parent directory to the path so we can import the services
sys.path.append(str(Path(__file__).parent.parent))

print("Environment variables:")
print("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT:", os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"))
print("AZURE_DOCUMENT_INTELLIGENCE_KEY is set:", os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY") is not None)

print("\nImporting modules...")
try:
    from services.document_intelligence import (
        DocumentIntelligenceClient,
        create_document_intelligence_client,
        TextExtractor,
        create_text_extractor,
        TableExtractor,
        create_table_extractor,
        ImageExtractor,
        create_image_extractor,
        HandwritingExtractor,
        create_handwriting_extractor,
        DocumentAnalyzer,
        create_document_analyzer
    )
    print("All modules imported successfully!")
    
    print("\nCreating client...")
    client = create_document_intelligence_client()
    print("Client created successfully!")
    
    print("\nCreating extractors...")
    text_extractor = create_text_extractor(client)
    table_extractor = create_table_extractor(client)
    image_extractor = create_image_extractor(client)
    handwriting_extractor = create_handwriting_extractor(client)
    print("Extractors created successfully!")
    
    print("\nCreating document analyzer...")
    document_analyzer = create_document_analyzer(client)
    print("Document analyzer created successfully!")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    print(traceback.format_exc())
