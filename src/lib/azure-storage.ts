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

    // Upload through Azure Function
    const response = await fetch(`${AZURE_FUNCTION_URL}/api/upload`, {
      method: 'POST',
      headers: {
        'Content-Type': file.type || 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${file.name}"`
      },
      body: file
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Upload error response:', errorText);
      throw new Error(`Upload failed with status: ${response.status}`);
    }

    const { url } = await response.json();
    return url;
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
