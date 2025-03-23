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