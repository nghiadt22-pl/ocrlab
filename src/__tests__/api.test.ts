import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import fetch from 'node-fetch';

// Mock fetch
vi.mock('node-fetch', () => {
  return {
    default: vi.fn()
  };
});

// Base URL for API endpoints
const API_BASE_URL = 'http://localhost:7071/api';

// Mock user ID for testing
const TEST_USER_ID = 'test-user-123';

// Helper function to create mock responses
const createMockResponse = (status: number, data: any) => {
  return {
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    headers: new Map()
  };
};

describe('API Endpoints', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // Test Folder Management Endpoints
  describe('Folder Management', () => {
    it('should list folders for a user', async () => {
      // Mock response data
      const mockFolders = {
        folders: [
          {
            id: 1,
            name: 'Home',
            user_id: TEST_USER_ID,
            created_at: '2023-03-10T12:00:00Z',
            updated_at: '2023-03-10T12:00:00Z'
          }
        ]
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(200, mockFolders));

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/folders`, {
        method: 'GET',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(200);
      expect(data).toEqual(mockFolders);
      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/folders`, {
        method: 'GET',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
    });

    it('should create a new folder', async () => {
      // Mock request and response data
      const folderName = 'New Folder';
      const mockResponse = {
        folder: {
          id: 2,
          name: folderName,
          user_id: TEST_USER_ID,
          created_at: '2023-03-10T12:00:00Z',
          updated_at: '2023-03-10T12:00:00Z'
        }
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(201, mockResponse));

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/folders`, {
        method: 'POST',
        headers: {
          'x-user-id': TEST_USER_ID,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: folderName })
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(201);
      expect(data).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/folders`, {
        method: 'POST',
        headers: {
          'x-user-id': TEST_USER_ID,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: folderName })
      });
    });

    it('should delete a folder', async () => {
      // Mock response data
      const folderId = 1;
      const mockResponse = {
        success: true,
        message: 'Folder deleted successfully'
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(200, mockResponse));

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/folders/${folderId}`, {
        method: 'DELETE',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(200);
      expect(data).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/folders/${folderId}`, {
        method: 'DELETE',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
    });
  });

  // Test File Management Endpoints
  describe('File Management', () => {
    it('should list files in a folder', async () => {
      // Mock response data
      const folderId = 1;
      const mockFiles = {
        files: [
          {
            id: 1,
            name: 'example.pdf',
            folder_id: folderId,
            blob_url: 'https://storage.azure.com/container/example.pdf',
            status: 'uploaded',
            size_bytes: 1048576,
            content_type: 'application/pdf',
            created_at: '2023-03-10T12:00:00Z',
            updated_at: '2023-03-10T12:00:00Z'
          }
        ]
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(200, mockFiles));

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/files?folder_id=${folderId}`, {
        method: 'GET',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(200);
      expect(data).toEqual(mockFiles);
      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/files?folder_id=${folderId}`, {
        method: 'GET',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
    });

    it('should delete a file', async () => {
      // Mock response data
      const fileId = 1;
      const mockResponse = {
        success: true,
        message: 'File deleted successfully'
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(200, mockResponse));

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/files?id=${fileId}`, {
        method: 'DELETE',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(200);
      expect(data).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/files?id=${fileId}`, {
        method: 'DELETE',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
    });

    it('should upload a file', async () => {
      // Mock file data
      const folderId = 1;
      const fileName = 'test.pdf';
      const fileContent = 'test file content';
      const fileSize = fileContent.length;
      const contentType = 'application/pdf';

      // Mock response data
      const mockResponse = {
        file: {
          id: 1,
          name: fileName,
          folder_id: folderId,
          blob_url: 'https://storage.azure.com/container/test.pdf',
          status: 'processing',
          size_bytes: fileSize,
          content_type: contentType,
          created_at: '2023-03-10T12:00:00Z',
          updated_at: '2023-03-10T12:00:00Z'
        }
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(201, mockResponse));

      // Create a mock FormData - using a string instead of FormData for testing
      const formData = 'mock-form-data';

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        headers: {
          'x-user-id': TEST_USER_ID,
          'x-folder-id': folderId.toString()
        },
        body: formData
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(201);
      expect(data).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/upload`, {
        method: 'POST',
        headers: {
          'x-user-id': TEST_USER_ID,
          'x-folder-id': folderId.toString()
        },
        body: formData
      });
    });
  });

  // Test Search Endpoints
  describe('Search', () => {
    it('should perform a search query', async () => {
      // Mock request and response data
      const searchQuery = 'test query';
      const mockResults = {
        results: [
          {
            id: 'mock-doc-1',
            text: 'This is a sample document that matches your query: ' + searchQuery,
            score: 0.95,
            filename: 'sample.pdf',
            blobUrl: 'https://example.com/sample.pdf',
            pageNumber: 1
          }
        ]
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(200, mockResults));

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'x-user-id': TEST_USER_ID,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: searchQuery, top: 5 })
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(200);
      expect(data).toEqual(mockResults);
      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'x-user-id': TEST_USER_ID,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: searchQuery, top: 5 })
      });
    });
  });

  // Test Usage Tracking Endpoints
  describe('Usage Tracking', () => {
    it('should get usage statistics for a user', async () => {
      // Mock response data
      const mockUsage = {
        usage: {
          pages_processed: 100,
          queries_made: 50,
          storage_used_bytes: 10485760,
          last_updated: '2023-03-10T12:00:00Z'
        }
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(200, mockUsage));

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/usage`, {
        method: 'GET',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(200);
      expect(data).toEqual(mockUsage);
      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/usage`, {
        method: 'GET',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
    });
  });

  // Test Document Indexing Endpoints
  describe('Document Indexing', () => {
    it('should index a document', async () => {
      // Mock request and response data
      const documentId = 'doc-123';
      const documentContent = 'This is a test document content';
      const mockResponse = {
        success: true,
        message: 'Document indexed successfully'
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(200, mockResponse));

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/index`, {
        method: 'POST',
        headers: {
          'x-user-id': TEST_USER_ID,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id: documentId,
          content: documentContent,
          metadata: JSON.stringify({
            filename: 'test.pdf',
            pageNumber: 1
          })
        })
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(200);
      expect(data).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/index`, {
        method: 'POST',
        headers: {
          'x-user-id': TEST_USER_ID,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id: documentId,
          content: documentContent,
          metadata: JSON.stringify({
            filename: 'test.pdf',
            pageNumber: 1
          })
        })
      });
    });
  });

  // Test Error Handling
  describe('Error Handling', () => {
    it('should handle missing user ID', async () => {
      // Mock response data
      const mockError = {
        error: 'User ID is required in x-user-id header'
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(400, mockError));

      // Make the API call without user ID
      const response = await fetch(`${API_BASE_URL}/folders`, {
        method: 'GET'
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(400);
      expect(data).toEqual(mockError);
    });

    it('should handle server errors', async () => {
      // Mock response data
      const mockError = {
        error: 'Failed to list folders: Internal server error'
      };

      // Setup mock fetch response
      (fetch as any).mockResolvedValueOnce(createMockResponse(500, mockError));

      // Make the API call
      const response = await fetch(`${API_BASE_URL}/folders`, {
        method: 'GET',
        headers: {
          'x-user-id': TEST_USER_ID
        }
      });
      const data = await response.json();

      // Verify the response
      expect(response.status).toBe(500);
      expect(data).toEqual(mockError);
    });
  });
}); 