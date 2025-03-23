import os
import sys
import json
import requests
import time
import logging
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI

# Add function_app to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the service classes (excluding DocumentService)
from services.chunking import ChunkingService

# Load environment variables from function_app/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_process_document')

def process_document(file_path, mock_mode=False, use_direct_api=True):
    """Process a document and generate embeddings"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize services
    chunking_service = ChunkingService()
    
    # Initialize Azure AI Search client
    search_endpoint = os.environ.get("AZURE_AISEARCH_ENDPOINT")
    search_key = os.environ.get("AZURE_AISEARCH_KEY")
    search_index_name = os.environ.get("AZURE_AISEARCH_INDEX", "ocrlab_index")
    
    if not search_endpoint or not search_key:
        logger.error("Azure AI Search is not configured. Cannot proceed with document processing.")
        raise ValueError("Azure AI Search must be configured for document processing")
    
    search_client = SearchClient(search_endpoint, search_index_name, AzureKeyCredential(search_key))
    logger.info(f"Initialized Azure AI Search client with index: {search_index_name}")
    
    # Initialize Azure OpenAI client
    api_key = os.environ.get("AZURE_OPENAI_KEY") or os.environ.get("AZURE_OPENAI_API_KEY")
    api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
    deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
    
    if not api_key or not api_endpoint:
        raise ValueError("Azure OpenAI credentials not configured")
    
    openai_client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_endpoint,
        timeout=30.0
    )
    logger.info(f"Initialized Azure OpenAI client with deployment: {deployment}")
    
    # Initialize Document Intelligence client
    doc_endpoint = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT") or os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
    doc_key = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY") or os.environ.get("DOCUMENT_INTELLIGENCE_API_KEY")
    
    if not doc_endpoint or not doc_key:
        raise ValueError("Document Intelligence credentials not configured")
        
    document_intelligence_client = DocumentIntelligenceClient(doc_endpoint, AzureKeyCredential(doc_key))
    logger.info("Initialized Document Intelligence client")
    
    # Process document
    try:
        # Read and analyze document with Document Intelligence API directly
        logger.info(f"Analyzing document: {file_path}")
        
        with open(file_path, "rb") as document_file:
            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-layout", 
                body=document_file
            )
            result = poller.result()
            
        logger.info("Document analysis complete")
        
        # Extract content from the result
        document_text = extract_document_content(result)
        
        # Create chunks from document
        document_id = f"doc_{os.path.splitext(os.path.basename(file_path))[0]}"
        document_title = os.path.splitext(os.path.basename(file_path))[0]
        chunks = chunking_service.chunk_document(document_text, document_id, document_title)
        
        # Generate embeddings for chunks
        if not mock_mode:
            # Process one chunk at a time
            chunks_with_embeddings = []
            processed_count = 0
            
            for chunk_index, chunk in enumerate(chunks):
                try:
                    # Add delay between requests to avoid rate limiting
                    if processed_count > 0:
                        time.sleep(2)  # 2 second delay between chunks
                    
                    logger.info(f"Processing chunk {chunk_index+1}/{len(chunks)} with ID {chunk.get('id', 'unknown')}")
                    
                    # Truncate text if it's too long
                    text = chunk["text"]
                    max_text_length = 8000
                    if len(text) > max_text_length:
                        logger.warning(f"Text too long ({len(text)} chars), truncating to {max_text_length}")
                        text = text[:max_text_length]
                    
                    # Generate embedding
                    response = openai_client.embeddings.create(
                        input=text,
                        model=deployment
                    )
                    
                    # Add embedding to the chunk
                    chunk["vector"] = response.data[0].embedding
                    chunks_with_embeddings.append(chunk)
                    processed_count += 1
                    
                    logger.info(f"Successfully processed chunk {processed_count}/{len(chunks)}")
                    
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk {chunk_index+1}/{len(chunks)}: {str(e)}")
            
            logger.info(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")
            
            # Save embeddings to file for inspection
            output_dir = os.path.dirname(file_path)
            output_file = os.path.join(output_dir, f"{os.path.basename(file_path)}_embeddings.json")
            
            with open(output_file, 'w') as f:
                json.dump(chunks_with_embeddings, f, indent=2)
                
            logger.info(f"Saved embeddings to {output_file}")
            
            # Index chunks to Azure AI Search
            user_id = os.environ.get("TEST_USER_ID", "test_user")
            
            # Prepare search documents
            search_documents = []
            
            for chunk in chunks_with_embeddings:
                # Create the search document
                search_document = {
                    "chunk_id": chunk["id"],  # Primary key field
                    "text_parent_id": chunk["parent_id"],
                    "chunk": chunk["text"],
                    "title": chunk["document_title"],
                    "header_1": chunk.get("document_title", ""),  # Use document title as header_1
                    "header_2": f"Page {chunk['page']}",     # Use page number as header_2
                    "header_3": chunk["type"].capitalize(),   # Use type as header_3
                    "content_vector": chunk["vector"],
                    "user_id": user_id  # Include user_id for multi-tenancy
                }
                search_documents.append(search_document)
            
            # Index in batches
            batch_size = 1000
            indexed_count = 0
            failed_count = 0
            
            for i in range(0, len(search_documents), batch_size):
                batch = search_documents[i:i + batch_size]
                logger.info(f"Uploading batch of {len(batch)} documents to search index")
                
                upload_result = search_client.upload_documents(documents=batch)
                
                success_count = len([r for r in upload_result if r.succeeded])
                batch_failed_count = len([r for r in upload_result if not r.succeeded])
                
                indexed_count += success_count
                failed_count += batch_failed_count
                
                logger.info(f"Batch upload results: {success_count} succeeded, {batch_failed_count} failed")
                
                # If any failed, log detailed errors
                if batch_failed_count > 0:
                    for i, result in enumerate(upload_result):
                        if not result.succeeded:
                            logger.error(f"Error indexing document {i}: {result.status_code} - {result.message}")
            
            result = {
                "total_count": len(search_documents),
                "indexed_count": indexed_count,
                "failed_count": failed_count
            }
            
            logger.info(f"Indexed chunks to Azure AI Search: {result}")
            
            # Return the document ID for future reference
            return {
                "document_id": document_id,
                "chunks_count": len(chunks_with_embeddings),
                "indexed_count": indexed_count,
                "user_id": user_id
            }
        else:
            logger.info("Mock mode enabled, skipping embedding generation and indexing")
            return {
                "document_id": document_id,
                "chunks_count": len(chunks),
                "indexed_count": 0,
                "user_id": os.environ.get("TEST_USER_ID", "test_user"),
                "mock_mode": True
            }
            
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

def extract_document_content(result):
    """Extract content from document result with structure information"""
    structured_content = {
        "paragraphs": [],
        "tables": [],
        "figures": [],
        "handwriting": []
    }
    
    # Extract paragraphs
    for paragraph in result.paragraphs:
        structured_content["paragraphs"].append({
            "text": paragraph.content,
            "page": paragraph.bounding_regions[0].page_number if paragraph.bounding_regions else 1,
            "confidence": paragraph.confidence if hasattr(paragraph, 'confidence') else 1.0
        })
        
    # Extract tables
    for table in result.tables:
        table_content = []
        for row_idx in range(table.row_count):
            row_content = []
            for col_idx in range(table.column_count):
                cell_content = ""
                for cell in table.cells:
                    if cell.row_index == row_idx and cell.column_index == col_idx:
                        cell_content = cell.content
                        break
                row_content.append(cell_content)
            table_content.append(row_content)
        
        structured_content["tables"].append({
            "content": table_content,
            "page": table.bounding_regions[0].page_number if table.bounding_regions else 1,
            "row_count": table.row_count,
            "column_count": table.column_count
        })
    
    # Extract figures/images with captions
    for page in result.pages:
        for figure_idx, figure in enumerate(getattr(page, 'figures', [])):
            caption = f"Figure {figure_idx+1}"
            # If OCR was performed on the figure, include that text
            figure_text = ""
            if hasattr(figure, 'content'):
                figure_text = figure.content
            
            structured_content["figures"].append({
                "text": figure_text,
                "caption": caption,
                "page": page.page_number
            })
    
    return structured_content

def vector_search(query, top_k=3):
    """Perform vector search using Azure AI Search"""
    # Initialize Azure AI Search client
    search_endpoint = os.environ.get("AZURE_AISEARCH_ENDPOINT")
    search_key = os.environ.get("AZURE_AISEARCH_KEY")
    search_index_name = os.environ.get("AZURE_AISEARCH_INDEX", "ocrlab_index")
    
    if not search_endpoint or not search_key:
        logger.error("Azure AI Search is not configured. Cannot perform vector search.")
        raise ValueError("Azure AI Search must be configured for vector search")
    
    search_client = SearchClient(search_endpoint, search_index_name, AzureKeyCredential(search_key))
    
    # Initialize Azure OpenAI client
    api_key = os.environ.get("AZURE_OPENAI_KEY") or os.environ.get("AZURE_OPENAI_API_KEY")
    api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
    deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
    
    if not api_key or not api_endpoint:
        raise ValueError("Azure OpenAI credentials not configured")
    
    openai_client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_endpoint,
        timeout=30.0
    )
    
    # Generate embedding for query
    response = openai_client.embeddings.create(
        input=query,
        model=deployment
    )
    query_embedding = response.data[0].embedding
    
    # Get test user ID from environment
    user_id = os.environ.get("TEST_USER_ID", "test_user")
    
    # Build filter expression for user_id (multi-tenancy)
    filter_expression = f"user_id eq '{user_id}'"
    
    # Define vector query
    vector_queries = [
        {
            "vector": query_embedding,
            "k": top_k,
            "fields": "content_vector",
            "kind": "vector"
        }
    ]
    
    # Execute search
    search_results = search_client.search(
        search_text=None,  # No text search
        vector_queries=vector_queries,
        filter=filter_expression,
        top=top_k,
        include_total_count=True
    )
    
    # Process results
    results = []
    for result in search_results:
        results.append({
            "text": result.get("chunk", ""),
            "page": int(result.get("header_2", "Page 0").replace("Page ", "")) if result.get("header_2") else 0,
            "type": result.get("header_3", "Unknown").lower() if result.get("header_3") else "unknown",
            "score": result.get("@search.score", 0.0),
            "document_title": result.get("title", ""),
            "parent_id": result.get("text_parent_id", "")
        })
    
    return results

def hybrid_search(query, top_k=3):
    """Perform hybrid search (text + vector) using Azure AI Search"""
    # Initialize Azure AI Search client
    search_endpoint = os.environ.get("AZURE_AISEARCH_ENDPOINT")
    search_key = os.environ.get("AZURE_AISEARCH_KEY")
    search_index_name = os.environ.get("AZURE_AISEARCH_INDEX", "ocrlab_index")
    
    if not search_endpoint or not search_key:
        logger.error("Azure AI Search is not configured. Cannot perform hybrid search.")
        raise ValueError("Azure AI Search must be configured for hybrid search")
    
    search_client = SearchClient(search_endpoint, search_index_name, AzureKeyCredential(search_key))
    
    # Initialize Azure OpenAI client
    api_key = os.environ.get("AZURE_OPENAI_KEY") or os.environ.get("AZURE_OPENAI_API_KEY")
    api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
    deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
    
    if not api_key or not api_endpoint:
        raise ValueError("Azure OpenAI credentials not configured")
    
    openai_client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_endpoint,
        timeout=30.0
    )
    
    # Generate embedding for query
    response = openai_client.embeddings.create(
        input=query,
        model=deployment
    )
    query_embedding = response.data[0].embedding
    
    # Get test user ID from environment
    user_id = os.environ.get("TEST_USER_ID", "test_user")
    
    # Build filter expression for user_id (multi-tenancy)
    filter_expression = f"user_id eq '{user_id}'"
    
    # Define vector query
    vector_queries = [
        {
            "vector": query_embedding,
            "k": top_k,
            "fields": "content_vector",
            "kind": "vector"
        }
    ]
    
    # Execute search
    search_results = search_client.search(
        search_text=query,  # Include text search for hybrid
        vector_queries=vector_queries,
        filter=filter_expression,
        top=top_k,
        include_total_count=True
    )
    
    # Process results
    results = []
    for result in search_results:
        results.append({
            "text": result.get("chunk", ""),
            "page": int(result.get("header_2", "Page 0").replace("Page ", "")) if result.get("header_2") else 0,
            "type": result.get("header_3", "Unknown").lower() if result.get("header_3") else "unknown",
            "score": result.get("@search.score", 0.0),
            "document_title": result.get("title", ""),
            "parent_id": result.get("text_parent_id", "")
        })
    
    return results

if __name__ == "__main__":
    logger.info("Started document processing test")
    
    try:
        # Process a PDF document
        pdf_path = "../../test_pdfs/deloitte-tech-risk-sector-banking_part_1.pdf"
        
        # Process with direct API approach for more reliable results
        result = process_document(pdf_path, mock_mode=False, use_direct_api=True)
        
        logger.info(f"Document processing complete: {result}")
        
        # Test vector search
        logger.info("Testing vector search")
        vector_results = vector_search("What are the technology risks in banking?", top_k=3)
        
        print("\nVector Search Results:")
        for i, result in enumerate(vector_results):
            print(f"{i+1}. Score: {result['score']:.4f}")
            print(f"   Text: {result['text'][:200]}...")
            print()
        
        # Test hybrid search
        logger.info("Testing hybrid search")
        hybrid_results = hybrid_search("technology risks banking", top_k=3)
        
        print("\nHybrid Search Results:")
        for i, result in enumerate(hybrid_results):
            print(f"{i+1}. Score: {result['score']:.4f}")
            print(f"   Text: {result['text'][:200]}...")
            print()
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise 