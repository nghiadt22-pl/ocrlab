import { toast } from 'sonner';

// Get Azure Function URL from environment
// const AZURE_FUNCTION_URL = import.meta.env.VITE_AZURE_FUNCTION_URL || 'http://localhost:7071';
const AZURE_FUNCTION_URL = import.meta.env.VITE_AZURE_FUNCTION_URL || 'https://testpl.azurewebsites.net';

/**
 * Uploads a file to Azure Blob Storage through Azure Function
 * @param file The file to upload
 * @param progressCallback Optional callback to track upload progress
 * @returns The URL of the uploaded blob
 */
export async function uploadFileToBlob(
  file: File,
  progressCallback?: (progress: number) => void
): Promise<string> {
  try {
    console.log('Starting file upload to Azure Blob Storage:', file.name);

    // Mock user ID and folder ID (in a real app, these would come from auth and UI)
    const userId = 'test-user-1';
    const folderId = '1';

    // Create FormData and append the file
    const formData = new FormData();
    formData.append('file', file);

    // Upload through Azure Function
    const response = await fetch(`${AZURE_FUNCTION_URL}/api/upload`, {
      method: 'POST',
      headers: {
        // Note: Don't set Content-Type when using FormData, browser will set it with the boundary
        'x-user-id': userId,  // Add the required x-user-id header
        'x-folder-id': folderId // Add the required x-folder-id header
      },
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Upload error response:', errorText);
      throw new Error(`Upload failed with status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Upload response:', result);
    
    // Check if the response has the expected structure
    if (result && result.file && result.file.blob_url) {
      return result.file.blob_url;
    } else if (result && result.url) {
      return result.url;
    } else {
      console.error('Unexpected response format:', result);
      throw new Error('Unexpected response format from upload API');
    }
  } catch (error) {
    console.error('Error uploading file to Azure Blob Storage:', error);
    toast.error('Failed to upload file to Azure Blob Storage');
    throw error;
  }
}

/**
 * Generates a URL for accessing the blob
 */
export function generateSasUrl(blobUrl: string): string {
  return blobUrl;
}
