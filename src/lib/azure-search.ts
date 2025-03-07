import { ProcessedDocument, SearchResult, SearchRequest } from './types';
import { toast } from 'sonner';

// Get Azure Function URL from environment
const AZURE_FUNCTION_URL = import.meta.env.VITE_AZURE_FUNCTION_URL || 'https://testpl.azurewebsites.net';

/**
 * Indexes a document in Azure Search through Azure Function
 * @param document The document to index
 * @param blobUrl The URL of the uploaded blob
 */
export async function indexDocumentInSearch(document: ProcessedDocument, blobUrl: string): Promise<void> {
  try {
    // Prepare the document for indexing
    const searchDocument = {
      id: document.id,
      content: document.extractedContent.map(item => {
        if (item.type === 'table' && Array.isArray(item.content)) {
          return (item.content as string[][]).map(row => row.join(' ')).join(' ');
        }
        return String(item.content);
      }).join(' '),
      metadata: JSON.stringify({
        filename: document.filename,
        processedAt: document.processedAt.toISOString(),
        blobUrl: blobUrl
      })
    };

    // Send to Azure Function
    const response = await fetch(`${AZURE_FUNCTION_URL}/api/index`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(searchDocument)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to index document: ${errorText}`);
    }
  } catch (error) {
    console.error('Error indexing document:', error);
    toast.error('Failed to index document in search');
    throw error;
  }
}

/**
 * Converts a processed document to search documents
 * @param document The processed document
 * @param blobUrl The URL of the uploaded blob
 * @returns An array of search documents
 */
function convertToSearchDocuments(
  document: ProcessedDocument,
  blobUrl: string
): SearchDocument[] {
  return document.extractedContent.map(item => {
    let content = '';
    
    // Convert content based on type
    if (item.type === 'table' && Array.isArray(item.content)) {
      content = item.content.map(row => row.join(' ')).join(' ');
    } else if (typeof item.content === 'string') {
      content = item.content;
    }
    
    return {
      id: `${document.id}-${item.id}`,
      filename: document.filename,
      content,
      pageNumber: item.pageNumber,
      contentType: item.type,
      confidence: item.confidence,
      blobUrl,
      processedAt: document.processedAt.toISOString()
    };
  });
}

/**
 * Indexes documents in Azure AI Search
 * @param documents The documents to index
 * @returns A boolean indicating whether the operation was successful
 */
async function indexDocuments(documents: SearchDocument[]): Promise<boolean> {
  try {
    // Don't proceed if there are no documents
    if (documents.length === 0) {
      return true;
    }
    
    const url = `${AZURE_AISEARCH_ENDPOINT}/indexes/${AZURE_AISEARCH_INDEX}/docs/index?api-version=2020-06-30`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api-key': AZURE_AISEARCH_KEY
      },
      body: JSON.stringify({ value: documents })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Azure Search API error:', errorData);
      throw new Error(`Azure Search API error: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('Azure Search indexing result:', result);
    
    return true;
  } catch (error) {
    console.error('Error in indexDocuments:', error);
    throw error;
  }
}

/**
 * Searches for documents in Azure AI Search
 * @param searchRequest The search request containing query and/or vector
 * @returns The search results
 */
export async function searchDocuments(searchRequest: SearchRequest): Promise<SearchResult[]> {
  try {
    // Validate the request
    if (!searchRequest.query && !searchRequest.vector) {
      throw new Error('Either query or vector must be provided');
    }

    if (searchRequest.vector && searchRequest.vector.length !== 1536) {
      throw new Error('Vector must have 1536 dimensions');
    }

    const response = await fetch(`${AZURE_FUNCTION_URL}/api/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...searchRequest,
        select: ['id', 'content', 'metadata'] // Always select these fields
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Search failed: ${errorText}`);
    }

    const result = await response.json();
    return result.value;
  } catch (error) {
    console.error('Error searching documents:', error);
    toast.error('Failed to search documents');
    throw error;
  }
}
