import re
import logging
import uuid
from typing import List, Dict, Any, Tuple

class ChunkingService:
    def __init__(self, max_chunk_size=1500, min_chunk_size=100):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.logger = logging.getLogger('chunking_service')
    
    def chunk_document(self, structured_content, document_id, document_title):
        """Process document content into optimized chunks for embedding"""
        self.logger.info(f"Chunking document: {document_title} (ID: {document_id})")
        
        chunks = []
        
        # Process paragraphs - most important text content
        chunks.extend(self._chunk_paragraphs(structured_content["paragraphs"]))
        
        # Process tables - need special handling to preserve structure
        chunks.extend(self._chunk_tables(structured_content["tables"]))
        
        # Process figures - usually short text so keep together
        chunks.extend(self._chunk_figures(structured_content["figures"]))
        
        # Process handwriting - usually important so keep separate
        chunks.extend(self._chunk_handwriting(structured_content["handwriting"]))
        
        # Add metadata to each chunk
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            chunks[i]["id"] = chunk_id
            chunks[i]["parent_id"] = document_id
            chunks[i]["document_title"] = document_title
        
        self.logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def _chunk_paragraphs(self, paragraphs):
        """Chunk paragraphs with appropriate size constraints"""
        chunks = []
        current_chunk = {"text": "", "page": None, "type": "paragraph"}
        
        # Sort paragraphs by page number for better context preservation
        paragraphs = sorted(paragraphs, key=lambda p: p["page"])
        
        for paragraph in paragraphs:
            # Skip empty paragraphs
            if not paragraph["text"].strip():
                continue
                
            # If this paragraph would make the chunk too big, save current chunk and start a new one
            if len(current_chunk["text"]) + len(paragraph["text"]) > self.max_chunk_size and len(current_chunk["text"]) >= self.min_chunk_size:
                chunks.append(current_chunk)
                current_chunk = {"text": "", "page": paragraph["page"], "type": "paragraph"}
            
            # Add paragraph to current chunk
            if current_chunk["page"] is None:
                current_chunk["page"] = paragraph["page"]
                
            # Add a newline between paragraphs if there's already content
            if current_chunk["text"]:
                current_chunk["text"] += "\n\n"
                
            current_chunk["text"] += paragraph["text"]
            
        # Add the last chunk if it has content
        if current_chunk["text"] and len(current_chunk["text"]) >= self.min_chunk_size:
            chunks.append(current_chunk)
        elif current_chunk["text"]:
            # If the last chunk is too small, try to merge with the previous chunk
            if chunks:
                chunks[-1]["text"] += "\n\n" + current_chunk["text"]
            else:
                # If there's no previous chunk, just add it despite being small
                chunks.append(current_chunk)
        
        return chunks
    
    def _chunk_tables(self, tables):
        """Process tables into chunks"""
        chunks = []
        
        for table in tables:
            # Convert table to text representation
            table_text = self._table_to_text(table["content"])
            
            # For large tables, we might need to split them
            if len(table_text) > self.max_chunk_size:
                rows_per_chunk = max(1, table["row_count"] // ((len(table_text) // self.max_chunk_size) + 1))
                for i in range(0, table["row_count"], rows_per_chunk):
                    chunk_rows = table["content"][i:i + rows_per_chunk]
                    chunk_text = self._table_to_text(chunk_rows)
                    
                    chunks.append({
                        "text": f"Table (rows {i+1}-{min(i+rows_per_chunk, table['row_count'])} of {table['row_count']}):\n{chunk_text}",
                        "page": table["page"],
                        "type": "table"
                    })
            else:
                chunks.append({
                    "text": f"Table ({table['row_count']}x{table['column_count']}):\n{table_text}",
                    "page": table["page"],
                    "type": "table"
                })
            
        return chunks
    
    def _table_to_text(self, table_content):
        """Convert table content to text representation"""
        if not table_content:
            return ""
            
        # Get maximum width for each column to align properly
        col_widths = [0] * len(table_content[0])
        for row in table_content:
            for i, cell in enumerate(row):
                if i < len(col_widths):  # Protect against inconsistent row lengths
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Format the table as text
        separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"
        text_rows = [separator]
        
        for row in table_content:
            text_row = "|"
            for i, cell in enumerate(row):
                if i < len(col_widths):  # Protect against inconsistent row lengths
                    text_row += f" {str(cell):{col_widths[i]}} |"
            text_rows.append(text_row)
            text_rows.append(separator)
        
        return "\n".join(text_rows)
    
    def _chunk_figures(self, figures):
        """Process figures into chunks"""
        chunks = []
        
        for figure in figures:
            if not figure["text"].strip():
                continue
                
            chunks.append({
                "text": f"{figure['caption']}: {figure['text']}",
                "page": figure["page"],
                "type": "figure"
            })
            
        return chunks
    
    def _chunk_handwriting(self, handwriting):
        """Process handwriting into chunks"""
        chunks = []
        
        for item in handwriting:
            if not item["text"].strip():
                continue
                
            chunks.append({
                "text": f"Handwritten text: {item['text']}",
                "page": item["page"],
                "type": "handwriting"
            })
            
        return chunks


class HybridChunkingStrategy:
    """
    Hybrid Figure/Paragraph Chunking Strategy
    
    Treats identified figures as primary chunks. Treats paragraphs not belonging
    to any figure as separate chunks.
    """
    
    def __init__(self, max_chunk_size=1500, min_chunk_size=100):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.logger = logging.getLogger('hybrid_chunking_strategy')
    
    def chunk_document(self, analyze_result, document_id, document_title):
        """
        Process document using hybrid figure/paragraph chunking strategy
        
        Args:
            analyze_result: The raw analyze result from Azure Document Intelligence
            document_id: Unique identifier for the document
            document_title: Title of the document
            
        Returns:
            List of chunks with appropriate metadata
        """
        self.logger.info(f"Using hybrid chunking strategy for document: {document_title} (ID: {document_id})")
        
        # Initialize empty list for chunks
        chunks = []
        
        # Handle different result formats - some files have 'analyzeResult' wrapper
        if "analyzeResult" in analyze_result:
            result = analyze_result["analyzeResult"]
        else:
            result = analyze_result
        
        # Track which paragraphs have been included in figure chunks
        included_paragraphs = set()
        
        # Process figures first
        if "figures" in result and result["figures"]:
            figure_chunks = self._chunk_figures(result)
            
            # Update included paragraphs set
            for chunk in figure_chunks:
                if "metadata" in chunk and "included_paragraph_indices" in chunk["metadata"]:
                    included_paragraphs.update(chunk["metadata"]["included_paragraph_indices"])
            
            chunks.extend(figure_chunks)
        
        # Process paragraphs not included in figure chunks
        if "paragraphs" in result and result["paragraphs"]:
            paragraph_chunks = self._chunk_standalone_paragraphs(
                result["paragraphs"], 
                included_paragraphs
            )
            chunks.extend(paragraph_chunks)
        
        # Add document metadata to each chunk
        for i, chunk in enumerate(chunks):
            if "chunk_id" not in chunk:
                chunk["chunk_id"] = f"{document_id}_chunk_{i}"
            chunk["parent_id"] = document_id
            chunk["document_title"] = document_title
        
        self.logger.info(f"Created {len(chunks)} chunks using hybrid chunking strategy")
        return chunks
    
    def _chunk_figures(self, analyze_result):
        """
        Process figures into chunks
        
        For each figure:
        1. Collect all paragraphs referenced in its elements
        2. Concatenate content to form the text for the figure chunk
        3. Add appropriate metadata
        """
        chunks = []
        
        if "figures" not in analyze_result or not analyze_result["figures"]:
            return chunks
            
        for figure in analyze_result["figures"]:
            # Get the figure ID
            figure_id = figure.get("id", str(uuid.uuid4()))
            
            # Get the page number from bounding regions
            page_number = 1  # Default to page 1
            bounding_regions = []
            if "boundingRegions" in figure and figure["boundingRegions"]:
                bounding_regions = figure["boundingRegions"]
                page_number = figure["boundingRegions"][0].get("pageNumber", 1)
            
            # Collect elements (paragraphs) referenced by this figure
            elements_included = figure.get("elements", [])
            
            # Also include caption elements if available
            if "caption" in figure and "elements" in figure["caption"]:
                elements_included.extend(figure["caption"]["elements"])
            
            # Get the caption text if available
            caption_text = ""
            if "caption" in figure and "content" in figure["caption"]:
                caption_text = figure["caption"]["content"]
            
            # Collect paragraph content
            paragraph_contents = []
            included_paragraph_indices = []
            
            # Add caption first if available
            if caption_text:
                paragraph_contents.append(caption_text)
            
            # Process each paragraph referenced by this figure
            for element in elements_included:
                if element.startswith("/paragraphs/"):
                    # Extract paragraph index
                    paragraph_index = self._extract_paragraph_index(element)
                    
                    # Get paragraph content
                    if "paragraphs" in analyze_result and paragraph_index < len(analyze_result["paragraphs"]):
                        paragraph_content = self._get_paragraph_content(
                            analyze_result["paragraphs"], 
                            paragraph_index
                        )
                        
                        # Add to contents if not already there (e.g., caption might be duplicated)
                        if paragraph_content and paragraph_content not in paragraph_contents:
                            paragraph_contents.append(paragraph_content)
                            included_paragraph_indices.append(paragraph_index)
            
            # Create a chunk with all figure text
            figure_text = "\n".join(paragraph_contents)
            
            # Create chunk if there's content
            if figure_text.strip():
                chunks.append({
                    "chunk_id": f"figure_{figure_id}",
                    "chunk_type": "figure",
                    "page_number": page_number,
                    "bounding_regions": bounding_regions,
                    "content": figure_text,
                    "metadata": {
                        "figure_id": figure_id,
                        "included_paragraph_indices": included_paragraph_indices
                    }
                })
        
        return chunks
    
    def _chunk_standalone_paragraphs(self, paragraphs, included_paragraphs):
        """
        Process paragraphs that haven't been included in figure chunks
        
        Args:
            paragraphs: List of paragraphs from analyze_result
            included_paragraphs: Set of paragraph indices that have been included in figure chunks
            
        Returns:
            List of standalone paragraph chunks
        """
        chunks = []
        paragraph_index = 0
        
        # Filter out certain roles if needed
        filter_roles = []  # We'll keep all roles but add them to metadata
        
        for i, paragraph in enumerate(paragraphs):
            # Skip if this paragraph was included in a figure chunk
            if i in included_paragraphs:
                continue
                
            # Get paragraph content
            paragraph_content = paragraph.get("content", "").strip()
            if not paragraph_content:
                continue
                
            # Get page number and bounding regions
            page_number = 1
            bounding_regions = []
            if "boundingRegions" in paragraph and paragraph["boundingRegions"]:
                bounding_regions = paragraph["boundingRegions"]
                page_number = paragraph["boundingRegions"][0].get("pageNumber", 1)
            
            # Create metadata
            metadata = {}
            if "role" in paragraph:
                metadata["role"] = paragraph["role"]
            
            # Create a chunk for this paragraph
            chunks.append({
                "chunk_id": f"paragraph_{paragraph_index}",
                "chunk_type": "paragraph",
                "page_number": page_number,
                "bounding_regions": bounding_regions,
                "content": paragraph_content,
                "metadata": metadata
            })
            
            paragraph_index += 1
        
        return chunks
    
    def _extract_paragraph_index(self, element_ref):
        """Extract paragraph index from element reference"""
        # Element reference format is "/paragraphs/index"
        if element_ref.startswith("/paragraphs/"):
            try:
                return int(element_ref.split("/")[-1])
            except (ValueError, IndexError):
                self.logger.warning(f"Could not extract paragraph index from: {element_ref}")
                return -1
        return -1
    
    def _get_paragraph_content(self, paragraphs, index):
        """Get paragraph content by index"""
        if 0 <= index < len(paragraphs):
            return paragraphs[index].get("content", "").strip()
        return "" 