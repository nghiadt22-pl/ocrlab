import { ProcessedDocument, SearchRequest, SearchResponse, UploadStatus } from './types';
import { useAuth } from '@/hooks/use-auth';

// Define API base URL based on environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Define interfaces for API responses
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export interface Folder {
  id: number;
  name: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface File {
  id: number;
  name: string;
  folder_id: number;
  blob_url: string;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  size_bytes: number;
  content_type: string;
  created_at: string;
  updated_at: string;
}

export interface UsageStats {
  pages_processed: number;
  queries_made: number;
  storage_used_bytes: number;
}

// Helper function to handle API errors
const handleApiError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
};

// Function to get authentication token from Clerk
const getAuthToken = async (): Promise<string | null> => {
  try {
    // Get the token from Clerk
    // Using dynamic import to avoid issues with SSR
    const clerk = await import('@clerk/clerk-react');
    if (clerk && clerk.useAuth) {
      // We can't use hooks directly here, so we'll use localStorage as a fallback
      const token = localStorage.getItem('clerk-token');
      return token;
    }
    return null;
  } catch (error) {
    console.error('Error getting auth token:', error);
    return null;
  }
};

// Function to get user ID from Clerk
const getUserId = (): string | null => {
  try {
    // Get the user ID from localStorage (set during login)
    // In a real implementation, this would come directly from Clerk
    return localStorage.getItem('userId');
  } catch (error) {
    console.error('Error getting user ID:', error);
    return null;
  }
};

// Helper function to make API requests
const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> => {
  try {
    // Get authentication token from Clerk
    const token = await getAuthToken();
    
    // Set default headers
    const headers = {
      'Content-Type': 'application/json',
      'x-user-id': getUserId() || '',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers,
    };

    // Make the request
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      ...options,
      headers,
    });

    // Parse the response
    const data = await response.json();

    // Check for error response
    if (!response.ok) {
      return { error: data.error || `Error: ${response.status}` };
    }

    return { data };
  } catch (error) {
    return { error: handleApiError(error) };
  }
};

// Folder API functions
export const getFolders = async (): Promise<ApiResponse<Folder[]>> => {
  return apiRequest<Folder[]>('folders');
};

export const createFolder = async (name: string): Promise<ApiResponse<Folder>> => {
  return apiRequest<Folder>('folders', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
};

export const deleteFolder = async (folderId: number): Promise<ApiResponse<void>> => {
  return apiRequest<void>(`folders/${folderId}`, {
    method: 'DELETE',
  });
};

// File API functions
export const getFiles = async (folderId?: number): Promise<ApiResponse<File[]>> => {
  const queryParams = folderId ? `?folder_id=${folderId}` : '';
  return apiRequest<File[]>(`files${queryParams}`);
};

export const uploadFile = async (
  file: Blob,
  folderId: number,
  onProgress?: (status: UploadStatus) => void
): Promise<ApiResponse<{ file_id: number }>> => {
  try {
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder_id', folderId.toString());

    // Get authentication token
    const token = await getAuthToken();
    
    // Set headers
    const headers: HeadersInit = {
      'x-user-id': getUserId() || '',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };

    // Create upload request
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    // Parse response
    const data = await response.json();

    // Check for error
    if (!response.ok) {
      return { error: data.error || `Error: ${response.status}` };
    }

    return { data };
  } catch (error) {
    return { error: handleApiError(error) };
  }
};

export const deleteFile = async (fileId: number): Promise<ApiResponse<void>> => {
  return apiRequest<void>('files', {
    method: 'DELETE',
    body: JSON.stringify({ file_id: fileId }),
  });
};

export const getFileProcessingStatus = async (fileId: number): Promise<ApiResponse<{ status: string }>> => {
  return apiRequest<{ status: string }>(`processing-status/${fileId}`);
};

// Search API functions
export const searchDocuments = async (query: string, limit: number = 5): Promise<ApiResponse<SearchResponse>> => {
  const searchRequest: SearchRequest = {
    query,
  };

  return apiRequest<SearchResponse>('query', {
    method: 'POST',
    body: JSON.stringify({ query: searchRequest.query, n: limit }),
  });
};

// Usage API functions
export const getUsageStats = async (): Promise<ApiResponse<UsageStats>> => {
  return apiRequest<UsageStats>('usage');
};

export default {
  getFolders,
  createFolder,
  deleteFolder,
  getFiles,
  uploadFile,
  deleteFile,
  getFileProcessingStatus,
  searchDocuments,
  getUsageStats,
}; 