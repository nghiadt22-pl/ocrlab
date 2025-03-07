
import React, { useCallback, useState } from 'react';
import { FileIcon, UploadIcon, XIcon, ServerIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onFileSelected: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelected }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const validateAndSetFile = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Please select a PDF file');
      return;
    }
    
    if (file.size > 15 * 1024 * 1024) { // 15MB limit
      toast.error('File size exceeds 15MB limit');
      return;
    }
    
    setSelectedFile(file);
    toast.success('PDF file selected');
  };

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  }, []);

  const handleRemoveFile = () => {
    setSelectedFile(null);
  };

  const handleProcessFile = () => {
    if (selectedFile) {
      onFileSelected(selectedFile);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto animate-fade-in">
      <div 
        className={cn(
          "border-2 border-dashed rounded-xl p-8 transition-all duration-300 bg-white/50 backdrop-blur-sm",
          isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50",
          selectedFile ? "bg-white/70" : ""
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {!selectedFile ? (
          <div className="text-center">
            <div className="mb-4 flex justify-center">
              <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center">
                <UploadIcon className="h-8 w-8 text-primary animate-pulse-subtle" />
              </div>
            </div>
            <h3 className="text-lg font-medium mb-2">Drag & Drop your PDF file</h3>
            <p className="text-muted-foreground text-sm mb-2 max-w-md mx-auto">
              Supported file: PDF up to 15MB
            </p>
            <p className="text-muted-foreground text-xs mb-6 max-w-md mx-auto">
              Files will be stored in Azure Blob Storage and processed content will be indexed in Azure AI Search
            </p>
            
            <div className="relative">
              <Button 
                className="relative z-10 px-6"
              >
                Select PDF
                <input
                  type="file"
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  onChange={handleFileChange}
                  accept=".pdf"
                />
              </Button>
            </div>
          </div>
        ) : (
          <div className="animate-scale-in">
            <div className="flex items-center p-3 bg-background/50 rounded-lg border border-border">
              <div className="h-10 w-10 bg-primary/10 rounded-md flex items-center justify-center mr-3">
                <FileIcon className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1 truncate">
                <p className="font-medium truncate">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <Button 
                variant="ghost" 
                size="icon" 
                className="ml-2 text-muted-foreground hover:text-destructive"
                onClick={handleRemoveFile}
              >
                <XIcon className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="mt-6 flex justify-center">
              <Button onClick={handleProcessFile} className="px-6">
                <ServerIcon className="h-4 w-4 mr-2" />
                Process & Upload
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
