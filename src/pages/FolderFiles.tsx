import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileIcon, 
  FolderIcon, 
  UploadIcon, 
  MoreHorizontalIcon, 
  TrashIcon, 
  DownloadIcon,
  SearchIcon,
  ArrowLeftIcon,
  FileTextIcon,
  FileSpreadsheetIcon,
  PresentationIcon,
  ImageIcon,
  ArchiveIcon,
  HelpCircleIcon,
  ClockIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  Loader2Icon
} from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import Header from '@/components/Header';
import { toast } from 'sonner';
import FileUpload from '@/components/FileUpload';
import { useFiles } from '@/hooks/use-api';
import { File as ApiFile } from '@/lib/api';
import { UploadStatus } from '@/lib/types';

// Define our custom file interface with a different name to avoid conflicts with the browser's File type
interface DocumentFile {
  id: number;
  name: string;
  size: string;
  type: string;
  uploadedAt: Date;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  pages: number;
}

// Convert API file to DocumentFile
const convertApiFileToDocumentFile = (file: ApiFile): DocumentFile => {
  return {
    id: file.id,
    name: file.name,
    size: `${(file.size_bytes / 1024 / 1024).toFixed(1)} MB`,
    type: file.name.split('.').pop() || 'unknown',
    uploadedAt: new Date(file.created_at),
    status: file.status,
    pages: 0 // This would come from metadata in a real implementation
  };
};

const FolderFiles: React.FC = () => {
  const { folderId } = useParams<{ folderId: string }>();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<string>('all');
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadStatus>({ status: 'idle' });

  // Use the files API hook
  const { 
    files: apiFiles, 
    isLoading, 
    isError, 
    error, 
    uploadFile, 
    deleteFile,
    isUploading,
    isDeleting
  } = useFiles(folderId ? parseInt(folderId) : undefined);

  // Convert API files to DocumentFile format
  const files: DocumentFile[] = apiFiles.map(convertApiFileToDocumentFile);

  const handleDeleteFile = (fileId: number) => {
    deleteFile(fileId);
  };

  // Update the parameter type to use the browser's File type
  const handleFileSelected = async (browserFile: File) => {
    if (!folderId) return;
    
    // Track upload progress
    const handleProgress = (status: UploadStatus) => {
      setUploadProgress(status);
    };
    
    // Upload the file
    uploadFile({ 
      file: browserFile, 
      folderId: parseInt(folderId), 
      onProgress: handleProgress 
    });
    
    setIsUploadDialogOpen(false);
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return <FileTextIcon className="h-5 w-5 text-red-500" />;
      case 'xlsx':
      case 'xls':
      case 'csv':
        return <FileSpreadsheetIcon className="h-5 w-5 text-green-500" />;
      case 'pptx':
      case 'ppt':
        return <PresentationIcon className="h-5 w-5 text-orange-500" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <ImageIcon className="h-5 w-5 text-blue-500" />;
      case 'zip':
      case 'rar':
        return <ArchiveIcon className="h-5 w-5 text-purple-500" />;
      default:
        return <HelpCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <Loader2Icon className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'uploading':
        return <UploadIcon className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'error':
        return <AlertCircleIcon className="h-4 w-4 text-red-500" />;
      default:
        return <ClockIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const filteredFiles = files.filter(file => {
    // Filter by search query
    if (searchQuery && !file.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Filter by tab
    if (activeTab === 'all') return true;
    if (activeTab === 'complete' && file.status === 'complete') return true;
    if (activeTab === 'processing' && file.status === 'processing') return true;
    if (activeTab === 'error' && file.status === 'error') return true;
    
    return false;
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-24">
          <div className="flex justify-center items-center h-64">
            <Loader2Icon className="h-8 w-8 animate-spin text-primary" />
          </div>
        </main>
      </div>
    );
  }

  if (isError && error) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-24">
          <div className="flex flex-col justify-center items-center h-64 space-y-4">
            <AlertCircleIcon className="h-12 w-12 text-destructive" />
            <h2 className="text-xl font-semibold">Error loading files</h2>
            <p className="text-muted-foreground">{error.message}</p>
            <Button onClick={() => navigate('/folders')}>
              <ArrowLeftIcon className="h-4 w-4 mr-2" />
              Back to Folders
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center mb-6">
          <Button variant="ghost" onClick={() => navigate('/folders')} className="mr-2">
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Files in {folderId ? `Folder ${folderId}` : 'Unknown Folder'}</h1>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
          <div className="relative w-full md:w-96">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search files..." 
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <UploadIcon className="h-4 w-4 mr-2" />
                Upload Files
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload Files</DialogTitle>
                <DialogDescription>
                  Upload PDF files to process with OCR. Maximum file size is 100MB.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <FileUpload onFileSelected={handleFileSelected} />
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsUploadDialogOpen(false)}>
                  Cancel
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab} className="mb-6">
          <TabsList>
            <TabsTrigger value="all">All Files</TabsTrigger>
            <TabsTrigger value="complete">Processed</TabsTrigger>
            <TabsTrigger value="processing">Processing</TabsTrigger>
            <TabsTrigger value="error">Failed</TabsTrigger>
          </TabsList>
        </Tabs>

        {filteredFiles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredFiles.map((file) => (
              <Card key={file.id} className="overflow-hidden">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <div className="flex items-center space-x-2">
                      {getFileIcon(file.type)}
                      <div>
                        <CardTitle className="text-base">{file.name}</CardTitle>
                        <CardDescription>{file.size} • {file.pages} pages</CardDescription>
                      </div>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontalIcon className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>
                          <DownloadIcon className="h-4 w-4 mr-2" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          className="text-destructive"
                          onClick={() => handleDeleteFile(file.id)}
                          disabled={isDeleting}
                        >
                          <TrashIcon className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    <span>Uploaded {formatDate(file.uploadedAt)}</span>
                  </div>
                </CardContent>
                <CardFooter className="pt-2 border-t">
                  <div className="flex items-center text-sm">
                    {getStatusIcon(file.status)}
                    <span className="ml-1 capitalize">{file.status}</span>
                  </div>
                </CardFooter>
              </Card>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 space-y-4">
            <div className="bg-muted p-4 rounded-full">
              <FileIcon className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-medium">No files found</h3>
            {searchQuery ? (
              <p className="text-muted-foreground text-center max-w-md">
                No files match your search query. Try a different search or upload new files.
              </p>
            ) : (
              <p className="text-muted-foreground text-center max-w-md">
                You haven't uploaded any files to this folder yet. Upload files to start processing.
              </p>
            )}
            <Button onClick={() => setIsUploadDialogOpen(true)}>
              <UploadIcon className="h-4 w-4 mr-2" />
              Upload Files
            </Button>
          </div>
        )}
      </main>
    </div>
  );
};

export default FolderFiles; 