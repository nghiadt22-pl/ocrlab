import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api, { Folder, File, UsageStats } from '@/lib/api';
import { toast } from '@/components/ui/use-toast';
import { UploadStatus } from '@/lib/types';

// Folder hooks
export function useFolders() {
  const queryClient = useQueryClient();

  const foldersQuery = useQuery({
    queryKey: ['folders'],
    queryFn: async () => {
      const response = await api.getFolders();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data || [];
    },
  });

  const createFolderMutation = useMutation({
    mutationFn: async (name: string) => {
      const response = await api.createFolder(name);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['folders'] });
      toast({
        title: 'Folder created',
        description: 'Your folder has been created successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Error creating folder',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const deleteFolderMutation = useMutation({
    mutationFn: async (folderId: number) => {
      const response = await api.deleteFolder(folderId);
      if (response.error) {
        throw new Error(response.error);
      }
      return folderId;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['folders'] });
      toast({
        title: 'Folder deleted',
        description: 'Your folder has been deleted successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Error deleting folder',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  return {
    folders: foldersQuery.data || [],
    isLoading: foldersQuery.isLoading,
    isError: foldersQuery.isError,
    error: foldersQuery.error,
    createFolder: createFolderMutation.mutate,
    deleteFolder: deleteFolderMutation.mutate,
    isCreating: createFolderMutation.isPending,
    isDeleting: deleteFolderMutation.isPending,
  };
}

// File hooks
export function useFiles(folderId?: number) {
  const queryClient = useQueryClient();

  const filesQuery = useQuery({
    queryKey: ['files', folderId],
    queryFn: async () => {
      const response = await api.getFiles(folderId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data || [];
    },
    enabled: folderId !== undefined,
  });

  const uploadFileMutation = useMutation({
    mutationFn: async ({ 
      file, 
      folderId, 
      onProgress 
    }: { 
      file: Blob; 
      folderId: number; 
      onProgress?: (status: UploadStatus) => void;
    }) => {
      const response = await api.uploadFile(file, folderId, onProgress);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files', folderId] });
      toast({
        title: 'File uploaded',
        description: 'Your file has been uploaded and is being processed.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Error uploading file',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const deleteFileMutation = useMutation({
    mutationFn: async (fileId: number) => {
      const response = await api.deleteFile(fileId);
      if (response.error) {
        throw new Error(response.error);
      }
      return fileId;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files', folderId] });
      toast({
        title: 'File deleted',
        description: 'Your file has been deleted successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Error deleting file',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  return {
    files: filesQuery.data || [],
    isLoading: filesQuery.isLoading,
    isError: filesQuery.isError,
    error: filesQuery.error,
    uploadFile: uploadFileMutation.mutate,
    deleteFile: deleteFileMutation.mutate,
    isUploading: uploadFileMutation.isPending,
    isDeleting: deleteFileMutation.isPending,
  };
}

// Search hooks
export function useSearch() {
  const searchMutation = useMutation({
    mutationFn: async ({ query, limit }: { query: string; limit?: number }) => {
      const response = await api.searchDocuments(query, limit);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onError: (error: Error) => {
      toast({
        title: 'Error searching documents',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  return {
    search: searchMutation.mutate,
    results: searchMutation.data?.value || [],
    isSearching: searchMutation.isPending,
    isError: searchMutation.isError,
    error: searchMutation.error,
  };
}

// Usage hooks
export function useUsage() {
  const usageQuery = useQuery({
    queryKey: ['usage'],
    queryFn: async () => {
      const response = await api.getUsageStats();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
  });

  return {
    usage: usageQuery.data,
    isLoading: usageQuery.isLoading,
    isError: usageQuery.isError,
    error: usageQuery.error,
  };
} 