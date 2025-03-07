import { ExtractedItem, ProcessedDocument } from './types';
import { uploadFileToBlob } from './azure-storage';
import { indexDocumentInSearch } from './azure-search';
import { toast } from 'sonner';

// Azure Document Intelligence API credentials
const AZURE_ENDPOINT = "https://testpl.cognitiveservices.azure.com/";
const AZURE_API_KEY = "4Isi8XsQLdLY9SrbRSvsNv47A9CX4RKKZZrk3CPROhmYQic1UA49JQQJ99BAACqBBLyXJ3w3AAALACOGdjHl";

/**
 * Processes a PDF file using Azure Document Intelligence
 */
export async function processPdfDocument(
  file: File, 
  onProgress?: (progress: number) => void
): Promise<ProcessedDocument> {
  try {
    // Start progress indication
    onProgress?.(5);
    
    // Step 1: Upload the file to Azure Blob Storage
    const blobUrl = await uploadFileToBlob(file, (uploadProgress) => {
      // Map upload progress to 5-25% of the total progress
      const mappedProgress = 5 + (uploadProgress * 0.2);
      onProgress?.(mappedProgress);
    });
    onProgress?.(25);
    
    // Step 2: Submit the document for analysis
    const operationLocation = await submitDocumentForAnalysis(file);
    onProgress?.(35);
    
    // Step 3: Poll for results
    const result = await pollForResults(operationLocation);
    onProgress?.(75);
    
    // Step 4: Transform the results into our application format
    const extractedItems = transformAzureResults(result);
    onProgress?.(85);
    
    // Create the processed document
    const processedDocument = {
      id: generateId(),
      filename: file.name,
      extractedContent: extractedItems,
      processedAt: new Date()
    };
    
    try {
      // Step 5: Index the results in Azure AI Search
      await indexDocumentInSearch(processedDocument, blobUrl);
    } catch (indexError) {
      // Log the error but don't fail the whole process
      console.error('Error indexing in Azure AI Search:', indexError);
      toast.warning('Document processed successfully, but indexing for search failed.');
      // Continue execution - the document processing was successful
    }
    
    onProgress?.(100);
    
    // Return the processed document
    return processedDocument;
  } catch (error) {
    console.error('Error processing document:', error);
    toast.error('Failed to process document. Please try again.');
    throw error;
  }
}

/**
 * Submits a document to the Azure Document Intelligence API for analysis
 */
async function submitDocumentForAnalysis(file: File): Promise<string> {
  console.log('Submitting document for analysis...');
  
  // Create form data with the file
  const formData = new FormData();
  formData.append('file', file);
  
  // Make the API request
  const response = await fetch(`${AZURE_ENDPOINT}/formrecognizer/documentModels/prebuilt-layout:analyze?api-version=2023-07-31`, {
    method: 'POST',
    headers: {
      'Ocp-Apim-Subscription-Key': AZURE_API_KEY,
    },
    body: formData
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    console.error('Azure API error response:', errorText);
    throw new Error(`Azure API error: ${response.status} ${response.statusText}`);
  }
  
  // Get the operation location from the response headers
  const operationLocation = response.headers.get('operation-location');
  if (!operationLocation) {
    throw new Error('Azure API did not return an operation location');
  }
  
  console.log('Document submitted successfully, operation location:', operationLocation);
  return operationLocation;
}

/**
 * Polls the Azure API operation status until document processing is complete
 */
async function pollForResults(operationUrl: string): Promise<any> {
  console.log('Polling for results...');
  
  // Maximum number of polling attempts
  const maxAttempts = 60;
  // Polling interval in milliseconds (5 seconds)
  const pollingInterval = 5000;
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    // Make the API request to check status
    const response = await fetch(operationUrl, {
      method: 'GET',
      headers: {
        'Ocp-Apim-Subscription-Key': AZURE_API_KEY
      }
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Azure API error response:', errorText);
      throw new Error(`Azure API error: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    
    // Check if the operation is complete
    if (result.status === 'succeeded') {
      console.log('Document processing complete');
      return result;
    } else if (result.status === 'failed') {
      throw new Error(`Azure API operation failed: ${JSON.stringify(result.error)}`);
    }
    
    // Wait before the next polling attempt
    console.log(`Polling attempt ${attempt + 1}/${maxAttempts}, status: ${result.status}`);
    await new Promise(resolve => setTimeout(resolve, pollingInterval));
  }
  
  throw new Error('Document processing timed out after maximum polling attempts');
}

/**
 * Transforms Azure API results into the application's format
 */
function transformAzureResults(azureResult: any): ExtractedItem[] {
  console.log('Transforming Azure results...');
  
  const extractedItems: ExtractedItem[] = [];
  const analyzeResult = azureResult.analyzeResult;
  
  // Process paragraphs
  if (analyzeResult.paragraphs) {
    extractedItems.push(...analyzeResult.paragraphs.map((paragraph: any, index: number) => ({
      id: `paragraph-${index}`,
      type: 'paragraph' as const,
      content: paragraph.content,
      confidence: paragraph.confidence || 0.9,
      pageNumber: paragraph.boundingRegions?.[0]?.pageNumber || 1,
      boundingBox: paragraph.boundingRegions?.[0]?.polygon ? {
        x: paragraph.boundingRegions[0].polygon[0],
        y: paragraph.boundingRegions[0].polygon[1],
        width: paragraph.boundingRegions[0].polygon[2] - paragraph.boundingRegions[0].polygon[0],
        height: paragraph.boundingRegions[0].polygon[7] - paragraph.boundingRegions[0].polygon[1]
      } : undefined
    })));
  }
  
  // Process tables
  if (analyzeResult.tables) {
    extractedItems.push(...analyzeResult.tables.map((table: any, tableIndex: number) => {
      // Convert table to a 2D array format
      const rows: string[][] = [];
      
      // Determine table dimensions
      const rowCount = Math.max(...table.cells.map((cell: any) => cell.rowIndex + 1));
      const colCount = Math.max(...table.cells.map((cell: any) => cell.columnIndex + 1));
      
      // Initialize the 2D array with empty strings
      for (let i = 0; i < rowCount; i++) {
        rows[i] = Array(colCount).fill('');
      }
      
      // Fill in the table cells
      table.cells.forEach((cell: any) => {
        rows[cell.rowIndex][cell.columnIndex] = cell.content || '';
      });
      
      return {
        id: `table-${tableIndex}`,
        type: 'table' as const,
        content: rows,
        confidence: table.confidence || 0.9,
        pageNumber: table.boundingRegions?.[0]?.pageNumber || 1,
        boundingBox: table.boundingRegions?.[0]?.polygon ? {
          x: table.boundingRegions[0].polygon[0],
          y: table.boundingRegions[0].polygon[1],
          width: table.boundingRegions[0].polygon[2] - table.boundingRegions[0].polygon[0],
          height: table.boundingRegions[0].polygon[7] - table.boundingRegions[0].polygon[1]
        } : undefined
      };
    }));
  }
  
  // Process figures
  if (analyzeResult.documents) {
    const figureCandidates = analyzeResult.documents.flatMap((doc: any) => {
      return doc.fields || {};
    });
    
    // For now, we're using placeholder images since the actual images aren't directly accessible
    Object.keys(figureCandidates).forEach((key, index) => {
      if (figureCandidates[key].kind === 'image' || key.toLowerCase().includes('image')) {
        extractedItems.push({
          id: `figure-${index}`,
          type: 'figure' as const,
          content: 'https://placehold.co/600x400/png',
          confidence: 0.8,
          pageNumber: 1
        });
      }
    });
  }
  
  // Extract handwriting if available (may require specific model version)
  if (analyzeResult.styles) {
    const handwrittenTexts = [];
    
    // Find content with handwritten style
    analyzeResult.styles.forEach((style: any) => {
      if (style.confidence > 0.7 && style.isHandwritten) {
        const pageNumber = style.boundingRegions?.[0]?.pageNumber || 1;
        
        // Try to find corresponding text spans
        const textItems = analyzeResult.spans?.filter((span: any) => {
          return span.offset === style.span.offset && span.length === style.span.length;
        }) || [];
        
        textItems.forEach((item: any, index: number) => {
          handwrittenTexts.push({
            id: `handwriting-${handwrittenTexts.length}`,
            type: 'handwriting' as const,
            content: item.content || 'Handwritten text',
            confidence: style.confidence,
            pageNumber
          });
        });
      }
    });
    
    extractedItems.push(...handwrittenTexts);
  }
  
  console.log(`Extracted ${extractedItems.length} items:`, 
    `${extractedItems.filter(i => i.type === 'paragraph').length} paragraphs, `,
    `${extractedItems.filter(i => i.type === 'table').length} tables, `,
    `${extractedItems.filter(i => i.type === 'figure').length} figures, `,
    `${extractedItems.filter(i => i.type === 'handwriting').length} handwriting items.`
  );
  
  // If we didn't extract anything, add a fallback item
  if (extractedItems.length === 0) {
    extractedItems.push({
      id: 'fallback-1',
      type: 'paragraph',
      content: 'No content could be extracted from this document. This could be due to the document format or content quality.',
      confidence: 0.5,
      pageNumber: 1
    });
  }
  
  return extractedItems;
}

/**
 * Generates a random ID for the document
 */
function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}
