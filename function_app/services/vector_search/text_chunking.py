"""
Text Chunking Module

This module provides functionality for chunking document content into smaller pieces
for vector database storage and retrieval.
"""

import logging
import re
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


class TextChunker:
    """
    Class for chunking document content into smaller pieces.
    
    This class provides methods for dividing document content into chunks
    suitable for vector database storage and retrieval.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        include_metadata: bool = True
    ):
        """
        Initialize the TextChunker.
        
        Args:
            chunk_size: The target size (in characters) for each chunk.
            chunk_overlap: The number of characters to overlap between chunks.
            include_metadata: Whether to include metadata in chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.include_metadata = include_metadata
        logger.info(f"TextChunker initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    
    def chunk_document(self, document_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk document content into smaller pieces.
        
        Args:
            document_content: The document content, including paragraphs, tables, etc.
        
        Returns:
            List[Dict[str, Any]]: A list of document chunks with metadata.
        """
        logger.info("Chunking document content")
        
        # Extract metadata from document content
        metadata = self._extract_metadata(document_content)
        
        # Get unified extracted items from document content
        extracted_items = document_content.get("extracted_items", [])
        
        # If no extracted items, try to create chunks from paragraphs
        if not extracted_items and "paragraphs" in document_content:
            chunks = self._chunk_paragraphs(document_content["paragraphs"], metadata)
            logger.info(f"Created {len(chunks)} chunks from paragraphs")
            return chunks
        
        # Process chunks by page
        page_groups = self._group_items_by_page(extracted_items)
        
        # Create chunks for each page
        all_chunks = []
        for page_num, items in page_groups.items():
            page_chunks = self._chunk_page_items(items, page_num, metadata)
            all_chunks.extend(page_chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(page_groups)} pages")
        return all_chunks
    
    def _extract_metadata(self, document_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from document content.
        
        Args:
            document_content: The document content.
        
        Returns:
            Dict[str, Any]: Metadata for the document.
        """
        # Extract basic metadata
        metadata = {
            "document_type": document_content.get("document_type", "unknown"),
            "language": document_content.get("language", "unknown"),
            "page_count": document_content.get("page_count", 0)
        }
        
        # Add summary if available
        if "summary" in document_content:
            metadata["summary"] = document_content["summary"]
        
        # Add keywords if available
        if "keywords" in document_content:
            metadata["keywords"] = document_content["keywords"]
        
        return metadata
    
    def _group_items_by_page(self, items: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """
        Group extracted items by page.
        
        Args:
            items: The extracted items.
        
        Returns:
            Dict[int, List[Dict[str, Any]]]: Items grouped by page number.
        """
        page_groups = {}
        for item in items:
            page_number = item.get("page_number", 1)
            if page_number not in page_groups:
                page_groups[page_number] = []
            page_groups[page_number].append(item)
        
        # Sort items within each page by position (top to bottom)
        for page_num, page_items in page_groups.items():
            page_groups[page_num] = self._sort_items_by_position(page_items)
        
        return page_groups
    
    def _sort_items_by_position(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort items by their position on the page (top to bottom).
        
        Args:
            items: The items to sort.
        
        Returns:
            List[Dict[str, Any]]: Sorted items.
        """
        # Sort items by their y-coordinate (top-left point of bounding box)
        def get_y_position(item):
            bounding_box = item.get("bounding_box")
            if bounding_box and len(bounding_box) >= 4:
                # Get the y-coordinate of the top-left point (second point)
                return bounding_box[1]
            return 0
        
        return sorted(items, key=get_y_position)
    
    def _chunk_page_items(
        self, items: List[Dict[str, Any]], page_number: int, metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create chunks from items on a page.
        
        Args:
            items: The items on the page.
            page_number: The page number.
            metadata: Document metadata.
        
        Returns:
            List[Dict[str, Any]]: Chunks from the page.
        """
        # Collect content from items
        content_items = []
        for item in items:
            item_type = item.get("type", "unknown")
            content = item.get("content", "")
            
            # Handle different item types
            if item_type == "paragraph":
                content_items.append({"type": "text", "content": content})
            elif item_type == "table":
                # Convert table to text representation
                if isinstance(content, list):
                    table_text = self._table_to_text(content)
                    content_items.append({"type": "table", "content": table_text})
            elif item_type == "figure":
                content_items.append({"type": "figure", "content": content})
            elif item_type == "handwriting":
                content_items.append({"type": "handwriting", "content": content})
        
        # Create chunks from content items
        chunks = self._create_chunks_from_content(content_items, page_number, metadata)
        return chunks
    
    def _table_to_text(self, table_rows: List[List[str]]) -> str:
        """
        Convert a table to a text representation.
        
        Args:
            table_rows: The table rows.
        
        Returns:
            str: Text representation of the table.
        """
        result = []
        for row in table_rows:
            if isinstance(row, list):
                result.append(" | ".join(str(cell) for cell in row))
        return "\n".join(result)
    
    def _create_chunks_from_content(
        self, content_items: List[Dict[str, Any]], page_number: int, metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create chunks from content items.
        
        Args:
            content_items: Content items to chunk.
            page_number: The page number.
            metadata: Document metadata.
        
        Returns:
            List[Dict[str, Any]]: Chunks created from content items.
        """
        # Combine content items into a single text
        combined_text = "\n\n".join(item["content"] for item in content_items)
        
        # Split text into chunks
        text_chunks = self._split_text(combined_text)
        
        # Create document chunks with metadata
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk = {
                "id": f"chunk-{page_number}-{i}",
                "text": chunk_text,
                "page_number": page_number
            }
            
            # Add metadata if configured
            if self.include_metadata:
                chunk["metadata"] = {
                    **metadata,
                    "page_number": page_number
                }
            
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_paragraphs(
        self, paragraphs: List[Dict[str, Any]], metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create chunks from paragraphs.
        
        Args:
            paragraphs: The paragraphs to chunk.
            metadata: Document metadata.
        
        Returns:
            List[Dict[str, Any]]: Chunks created from paragraphs.
        """
        # Group paragraphs by page
        page_groups = {}
        for para in paragraphs:
            page_number = para.get("page_number", 1)
            if page_number not in page_groups:
                page_groups[page_number] = []
            page_groups[page_number].append(para)
        
        # Create chunks for each page
        all_chunks = []
        for page_num, page_paras in page_groups.items():
            # Sort paragraphs by position
            sorted_paras = sorted(page_paras, key=lambda p: p.get("bounding_box", [0, 0, 0, 0])[1] if p.get("bounding_box") else 0)
            
            # Combine paragraph content
            combined_text = "\n\n".join(para.get("content", "") for para in sorted_paras)
            
            # Split text into chunks
            text_chunks = self._split_text(combined_text)
            
            # Create document chunks with metadata
            for i, chunk_text in enumerate(text_chunks):
                chunk = {
                    "id": f"chunk-{page_num}-{i}",
                    "text": chunk_text,
                    "page_number": page_num
                }
                
                # Add metadata if configured
                if self.include_metadata:
                    chunk["metadata"] = {
                        **metadata,
                        "page_number": page_num
                    }
                
                all_chunks.append(chunk)
        
        return all_chunks
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks of the specified size.
        
        Args:
            text: The text to split.
        
        Returns:
            List[str]: Chunks of text.
        """
        # If text is shorter than chunk size, return it as a single chunk
        if len(text) <= self.chunk_size:
            return [text]
        
        # Split text into chunks
        chunks = []
        start = 0
        while start < len(text):
            # Determine end position for this chunk
            end = start + self.chunk_size
            
            # Adjust end position to avoid splitting in the middle of a word or sentence
            if end < len(text):
                # Try to find a sentence boundary
                sentence_end = text.rfind(".", start, end)
                if sentence_end != -1 and sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Try to find a paragraph boundary
                    para_end = text.rfind("\n", start, end)
                    if para_end != -1 and para_end > start + self.chunk_size // 2:
                        end = para_end + 1
                    else:
                        # Try to find a word boundary
                        space = text.rfind(" ", start, end)
                        if space != -1:
                            end = space + 1
            
            # Extract the chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move to next position with overlap
            start = end - self.chunk_overlap
            if start <= 0 or start >= len(text):
                break
        
        return chunks


def create_text_chunker(
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    include_metadata: bool = True
) -> TextChunker:
    """
    Create a TextChunker.
    
    Args:
        chunk_size: The target size (in characters) for each chunk.
        chunk_overlap: The number of characters to overlap between chunks.
        include_metadata: Whether to include metadata in chunks.
    
    Returns:
        TextChunker: A TextChunker instance.
    """
    return TextChunker(chunk_size, chunk_overlap, include_metadata)
