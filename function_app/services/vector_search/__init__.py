"""
Vector Search Package

This package provides functionality for text chunking, embedding generation,
and vector database integration for the OCR Lab application.
"""

from .text_chunking import create_text_chunker, TextChunker
from .embeddings import create_embeddings_generator, EmbeddingsGenerator
from .vector_db import create_vector_database, VectorDatabase, MockVectorDatabase

__all__ = [
    'create_text_chunker',
    'TextChunker',
    'create_embeddings_generator',
    'EmbeddingsGenerator',
    'create_vector_database',
    'VectorDatabase',
    'MockVectorDatabase'
]
