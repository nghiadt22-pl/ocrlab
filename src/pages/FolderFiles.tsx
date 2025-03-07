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

// Mock data for folders
const mockFolders = [
  {
    id: '1',
    name: 'Home',
    documentCount: 5,
    createdAt: new Date('2023-01-15'),
  },
  {
    id: '2',
    name: 'Financial Reports',
    documentCount: 12,
    createdAt: new Date('2023-02-20'),
  },
  {
    id: '3',
    name: 'Contracts',
    documentCount: 8,
    createdAt: new Date('2023-03-10'),
  },
  {
    id: '4',
    name: 'Meeting Notes',
    documentCount: 3,
    createdAt: new Date('2023-04-05'),
  },
];

type FileStatus = 'processed' | 'processing' | 'error' | 'uploading';

// Define our custom file interface with a different name to avoid conflicts with the browser's File type
interface DocumentFile {
  id: string;
  name: string;
  size: string;
  type: string;
  uploadedAt: Date;
  status: FileStatus;
  pages: number;
}

// Mock data for files with the correct FileStatus type
const mockFiles: DocumentFile[] = [
  {
    id: '1',
    name: 'Q1 Financial Report.pdf',
    size: '2.4 MB',
    type: 'pdf',
    uploadedAt: new Date('2023-02-15'),
    status: 'processed',
    pages: 12
  },
  {
    id: '2',
    name: 'Employee Handbook.pdf',
    size: '5.1 MB',
    type: 'pdf',
    uploadedAt: new Date('2023-02-20'),
    status: 'processing',
    pages: 45
  },
  {
    id: '3',
    name: 'Project Proposal.pdf',
    size: '1.8 MB',
    type: 'pdf',
    uploadedAt: new Date('2023-03-05'),
    status: 'error',
    pages: 8
  },
  {
    id: '4',
    name: 'Meeting Minutes.pdf',
    size: '0.9 MB',
    type: 'pdf',
    uploadedAt: new Date('2023-03-10'),
    status: 'processed',
    pages: 4
  },
  {
    id: '5',
    name: 'Sales Presentation.pdf',
    size: '3.2 MB',
    type: 'pdf',
    uploadedAt: new Date('2023-03-15'),
    status: 'processed',
    pages: 18
  }
];

const FolderFiles: React.FC = () => {
  const { folderId } = useParams<{ folderId: string }>();
  const navigate = useNavigate();
  const [files, setFiles] = useState<DocumentFile[]>([]);
  const [folder, setFolder] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<string>('all');
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);

  useEffect(() => {
    // In a real app, we would fetch the folder and files from the API
    const foundFolder = mockFolders.find(f => f.id === folderId);
    if (foundFolder) {
      setFolder(foundFolder);
      setFiles(mockFiles);
    } else {
      toast.error('Folder not found');
      navigate('/folders');
    }
  }, [folderId, navigate]);

  const handleDeleteFile = (fileId: string, fileName: string) => {
    setFiles(files.filter(file => file.id !== fileId));
    toast.success(`File "${fileName}" deleted successfully`);
  };

  // Update the parameter type to use the browser's File type
  const handleFileSelected = async (browserFile: File) => {
    // In a real app, we would upload the file to the server
    toast.success(`File "${browserFile.name}" uploaded successfully`);
    setIsUploadDialogOpen(false);
    
    // Simulate adding a new file
    const newFile: DocumentFile = {
      id: Date.now().toString(),
      name: browserFile.name,
      // Convert bytes to MB safely
      size: `${(browserFile.size / 1024 / 1024).toFixed(1)} MB`,
      type: browserFile.name.split('.').pop() || 'unknown',
      uploadedAt: new Date(),
      status: 'processing',
      pages: 0
    };
    
    setFiles([newFile, ...files]);
    
    // Simulate processing completion after 3 seconds
    setTimeout(() => {
      setFiles(prevFiles => 
        prevFiles.map(f => 
          f.id === newFile.id 
            ? { ...f, status: 'processed', pages: Math.floor(Math.random() * 20) + 1 } 
            : f
        )
      );
      toast.success(`File "${browserFile.name}" processed successfully`);
    }, 3000);
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

  const getStatusIcon = (status: FileStatus) => {
    switch (status) {
      case 'processed':
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
    if (activeTab === 'processed' && file.status === 'processed') return true;
    if (activeTab === 'processing' && file.status === 'processing') return true;
    if (activeTab === 'error' && file.status === 'error') return true;
    
    return false;
  });

  if (!folder) {
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

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <div className="flex items-center mb-6">
          <Button 
            variant="ghost" 
            size="sm" 
            className="mr-2"
            onClick={() => navigate('/folders')}
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Folders
          </Button>
        </div>

        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 p-3 rounded-lg">
              <FolderIcon className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">{folder.name}</h1>
              <p className="text-muted-foreground">
                Created on {formatDate(folder.createdAt)}
              </p>
            </div>
          </div>
          <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <UploadIcon className="h-4 w-4" />
                Upload Files
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Upload Files</DialogTitle>
                <DialogDescription>
                  Upload PDF files to this folder for OCR processing
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <FileUpload onFileSelected={handleFileSelected} />
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="flex flex-col gap-6">
          <div className="flex flex-col sm:flex-row justify-between gap-4">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full sm:max-w-md">
              <TabsList className="grid grid-cols-4 w-full">
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="processed">Processed</TabsTrigger>
                <TabsTrigger value="processing">Processing</TabsTrigger>
                <TabsTrigger value="error">Error</TabsTrigger>
              </TabsList>
            </Tabs>
            <div className="relative w-full sm:max-w-xs">
              <SearchIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search files..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {filteredFiles.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 border border-dashed rounded-lg">
              <FileIcon className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No files found</h3>
              <p className="text-muted-foreground text-center max-w-md mb-6">
                {searchQuery 
                  ? `No files matching "${searchQuery}" were found in this folder.` 
                  : "This folder is empty. Upload files to get started."}
              </p>
              <Button onClick={() => setIsUploadDialogOpen(true)}>
                <UploadIcon className="h-4 w-4 mr-2" />
                Upload Files
              </Button>
            </div>
          ) : (
            <div className="border rounded-lg overflow-hidden">
              <div className="grid grid-cols-12 gap-4 p-4 bg-muted/50 text-sm font-medium">
                <div className="col-span-6">Name</div>
                <div className="col-span-1 text-center">Pages</div>
                <div className="col-span-2">Size</div>
                <div className="col-span-2">Uploaded</div>
                <div className="col-span-1 text-right">Actions</div>
              </div>
              <div className="divide-y">
                {filteredFiles.map((file) => (
                  <div key={file.id} className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-muted/20 transition-colors">
                    <div className="col-span-6 flex items-center gap-3">
                      <div className="flex-shrink-0">
                        {getFileIcon(file.type)}
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium truncate">{file.name}</p>
                        <div className="flex items-center text-xs text-muted-foreground">
                          {getStatusIcon(file.status)}
                          <span className="ml-1 capitalize">{file.status}</span>
                        </div>
                      </div>
                    </div>
                    <div className="col-span-1 text-center">
                      {file.status === 'processed' ? file.pages : '-'}
                    </div>
                    <div className="col-span-2">{file.size}</div>
                    <div className="col-span-2 text-sm text-muted-foreground">
                      {formatDate(file.uploadedAt)}
                    </div>
                    <div className="col-span-1 flex justify-end">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontalIcon className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {file.status === 'processed' && (
                            <DropdownMenuItem className="flex items-center gap-2 cursor-pointer">
                              <DownloadIcon className="h-4 w-4" />
                              Download
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem 
                            className="flex items-center gap-2 text-destructive cursor-pointer"
                            onClick={() => handleDeleteFile(file.id, file.name)}
                          >
                            <TrashIcon className="h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default FolderFiles; 