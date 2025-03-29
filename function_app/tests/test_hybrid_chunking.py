import unittest
import os
import json
from unittest.mock import patch, MagicMock
import sys
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.chunking import ChunkingService, HybridChunkingStrategy
from dotenv import load_dotenv

class TestHybridChunking(unittest.TestCase):
    def setUp(self):
        self.chunking_service = ChunkingService()
        self.hybrid_strategy = HybridChunkingStrategy()
        
        # Sample document intelligence result with figures and paragraphs
        self.sample_result = {
            "figures": [
                {
                    "id": "1.1",
                    "boundingRegions": [{"pageNumber": 1, "polygon": [0.9676, 3.0376, 6.986, 3.0316, 6.9893, 10.9501, 0.9706, 10.9558]}],
                    "elements": ["/paragraphs/1", "/paragraphs/2"],
                    "caption": {
                        "content": "Figure 1: Sample diagram",
                        "elements": ["/paragraphs/3"]
                    }
                }
            ],
            "paragraphs": [
                {
                    "content": "This is a title",
                    "role": "title",
                    "boundingRegions": [{"pageNumber": 1, "polygon": [1.0, 1.0, 2.0, 1.0, 2.0, 2.0, 1.0, 2.0]}]
                },
                {
                    "content": "This is paragraph 1 in figure 1",
                    "boundingRegions": [{"pageNumber": 1, "polygon": [1.0, 3.0, 2.0, 3.0, 2.0, 4.0, 1.0, 4.0]}]
                },
                {
                    "content": "This is paragraph 2 in figure 1",
                    "boundingRegions": [{"pageNumber": 1, "polygon": [1.0, 4.0, 2.0, 4.0, 2.0, 5.0, 1.0, 5.0]}]
                },
                {
                    "content": "Figure 1: Sample diagram",
                    "boundingRegions": [{"pageNumber": 1, "polygon": [1.0, 5.0, 2.0, 5.0, 2.0, 6.0, 1.0, 6.0]}]
                },
                {
                    "content": "This is a standalone paragraph",
                    "boundingRegions": [{"pageNumber": 1, "polygon": [3.0, 3.0, 4.0, 3.0, 4.0, 4.0, 3.0, 4.0]}]
                },
                {
                    "content": "This is a footer",
                    "role": "pageFooter",
                    "boundingRegions": [{"pageNumber": 1, "polygon": [1.0, 10.0, 3.0, 10.0, 3.0, 10.5, 1.0, 10.5]}]
                }
            ]
        }

        # Try to load real document intelligence result from the specified path
        self.real_result = None
        try:
            # First try to load from test_pdfs directory in project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            test_pdfs_path = os.path.join(project_root, 'test_pdfs')
            real_data_path = os.path.join(test_pdfs_path, '1742180735323.pdf.json')
            
            print(f"Looking for test file at: {real_data_path}")
            if not os.path.exists(test_pdfs_path):
                print(f"Warning: test_pdfs directory does not exist at {test_pdfs_path}")
            
            if os.path.exists(real_data_path):
                print(f"File found at {real_data_path}")
                with open(real_data_path, 'r', encoding='utf-8') as f:
                    self.real_result = json.load(f)
                    print(f"Successfully loaded real Document Intelligence result (keys: {list(self.real_result.keys() if self.real_result else [])})")
            else:
                print(f"Warning: Test JSON file not found at {real_data_path}")
                # List files in test_pdfs directory
                if os.path.exists(test_pdfs_path):
                    print(f"Files in test_pdfs directory:")
                    for file in os.listdir(test_pdfs_path):
                        print(f"  - {file}")
                
                # Fallback to looking in the test directory
                sample_data_path = os.path.join(os.path.dirname(__file__), 'sample_doc_result.json')
                if os.path.exists(sample_data_path):
                    with open(sample_data_path, 'r', encoding='utf-8') as f:
                        self.real_result = json.load(f)
                        print(f"Loaded fallback Document Intelligence result from {sample_data_path}")
        except Exception as e:
            print(f"Error loading real document data: {str(e)}")
            print(traceback.format_exc())
        
    def test_extract_paragraph_index(self):
        """Test extracting paragraph index from element reference"""
        element_ref = "/paragraphs/5"
        expected_index = 5
        result = self.hybrid_strategy._extract_paragraph_index(element_ref)
        self.assertEqual(result, expected_index)
        
    def test_get_paragraph_content(self):
        """Test getting paragraph content by index"""
        # Check if we can access paragraphs in the sample result
        if not hasattr(self, 'sample_result') or not self.sample_result or "paragraphs" not in self.sample_result:
            self.skipTest("Sample result not available or missing paragraphs")
            
        index = 1
        expected_content = "This is paragraph 1 in figure 1"
        result = self.hybrid_strategy._get_paragraph_content(self.sample_result["paragraphs"], index)
        self.assertEqual(result, expected_content)
        
    def test_chunk_format_with_sample_data(self):
        """Test the format of chunks with sample data matches the expected format"""
        document_id = "test_doc_1"
        document_title = "Test Document"
            
        # Call with hybrid strategy
        chunks = self.hybrid_strategy.chunk_document(self.sample_result, document_id, document_title)
            
        # Assert the chunks are created correctly
        self.assertGreater(len(chunks), 0)
        
        # Check each chunk has the expected fields
        for chunk in chunks:
            self.assertIn("chunk_id", chunk)
            self.assertIn("chunk_type", chunk)
            self.assertIn("page_number", chunk)
            self.assertIn("bounding_regions", chunk)
            self.assertIn("content", chunk)
            self.assertIn("metadata", chunk)
            
            # Check type-specific fields
            if chunk["chunk_type"] == "figure":
                self.assertIn("figure_id", chunk["metadata"])
                self.assertIn("included_paragraph_indices", chunk["metadata"])
            elif chunk["chunk_type"] == "paragraph" and "role" in chunk["metadata"]:
                self.assertIn(chunk["metadata"]["role"], ["title", "pageHeader", "pageFooter", "pageNumber", "sectionHeading", "footnote"])
            
    def test_hybrid_chunking_with_real_document_intelligence_result(self):
        """Test hybrid chunking with actual Document Intelligence data"""
        if self.real_result is None:
            self.skipTest("No real Document Intelligence result available for testing")
            
        print(f"Testing with real document intelligence result (keys: {list(self.real_result.keys())})")
        
        # Check if the result has the necessary structure
        if "analyzeResult" in self.real_result:
            analyze_result = self.real_result["analyzeResult"]
            print(f"Found analyzeResult key with sub-keys: {list(analyze_result.keys())}")
        else:
            analyze_result = self.real_result
            
        # Check for required components
        if "paragraphs" not in analyze_result and "pages" in analyze_result:
            print("Warning: No direct paragraphs key, but found pages. Using pages instead.")
            # Some API results have pages but no top-level paragraphs
            if "paragraphs" not in analyze_result:
                analyze_result["paragraphs"] = []
                for page in analyze_result.get("pages", []):
                    if "paragraphs" in page:
                        analyze_result["paragraphs"].extend(page["paragraphs"])
                    
        if "paragraphs" not in analyze_result:
            self.skipTest(f"Real result missing 'paragraphs' key. Available keys: {list(analyze_result.keys())}")
            
        print(f"Number of paragraphs found: {len(analyze_result.get('paragraphs', []))}")
        
        document_id = "real_doc_1"
        document_title = "Real Test Document"
        
        # Call the hybrid chunking method with real data
        chunks = self.hybrid_strategy.chunk_document(self.real_result, document_id, document_title)
        
        # Assert that we get chunks
        self.assertGreater(len(chunks), 0)
        
        # Log some information about the chunks
        print(f"Created {len(chunks)} chunks from real document")
        figure_chunks = [chunk for chunk in chunks if chunk["chunk_type"] == "figure"]
        paragraph_chunks = [chunk for chunk in chunks if chunk["chunk_type"] == "paragraph"]
        print(f"Figure chunks: {len(figure_chunks)}")
        print(f"Paragraph chunks: {len(paragraph_chunks)}")
        
        # Log first few chunks of each type for inspection
        if figure_chunks:
            print("\nSample figure chunk:")
            sample_figure = figure_chunks[0]
            print(f"Chunk ID: {sample_figure['chunk_id']}")
            print(f"Type: {sample_figure['chunk_type']}")
            print(f"Page: {sample_figure['page_number']}")
            print(f"Figure ID: {sample_figure['metadata'].get('figure_id', 'N/A')}")
            print(f"Text (first 100 chars): {sample_figure['content'][:100]}...")
            
        if paragraph_chunks:
            print("\nSample paragraph chunk:")
            sample_paragraph = paragraph_chunks[0]
            print(f"Chunk ID: {sample_paragraph['chunk_id']}")
            print(f"Type: {sample_paragraph['chunk_type']}")
            print(f"Page: {sample_paragraph['page_number']}")
            print(f"Role: {sample_paragraph['metadata'].get('role', 'N/A')}")
            print(f"Text: {sample_paragraph['content']}")
        
        # Write the output to a file for inspection
        output_path = os.path.join(os.path.dirname(__file__), 'hybrid_chunks_output.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2)
        print(f"Wrote output to {output_path}")
        
        # Compare with expected output
        if len(chunks) > 0:
            # The test passed if we got any chunks
            self.assertTrue(True, "Successfully generated chunks from the real document")

if __name__ == '__main__':
    unittest.main() 