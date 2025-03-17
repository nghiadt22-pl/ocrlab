"""
Azure Document Intelligence Service

This package provides functionality for interacting with Azure Document Intelligence,
including document analysis, text extraction, table extraction, image extraction,
and handwriting recognition.
"""

from .client import DocumentIntelligenceClient, create_document_intelligence_client
from .text_extraction import TextExtractor, create_text_extractor
from .table_extraction import TableExtractor, create_table_extractor
from .image_extraction import ImageExtractor, create_image_extractor
from .handwriting_extraction import HandwritingExtractor, create_handwriting_extractor
from .document_analyzer import DocumentAnalyzer, create_document_analyzer

__all__ = [
    'DocumentIntelligenceClient', 
    'create_document_intelligence_client',
    'TextExtractor',
    'create_text_extractor',
    'TableExtractor',
    'create_table_extractor',
    'ImageExtractor',
    'create_image_extractor',
    'HandwritingExtractor',
    'create_handwriting_extractor',
    'DocumentAnalyzer',
    'create_document_analyzer'
]
