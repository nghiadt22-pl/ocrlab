import React, { useState } from 'react';
import Header from '@/components/Header';
import FileUpload from '@/components/FileUpload';
import ProcessingView from '@/components/ProcessingView';
import ResultView from '@/components/ResultView';
import Search from '@/components/Search';
import { processPdfDocument } from '@/lib/azure-ai';
import { ProcessedDocument, UploadStatus } from '@/lib/types';
import { toast } from 'sonner';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const Index: React.FC = () => {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({ status: 'idle' });
  const [processedDocument, setProcessedDocument] = useState<ProcessedDocument | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'search'>('upload');

  const handleFileSelected = async (file: File) => {
    try {
      setUploadStatus({ 
        status: 'uploading', 
        progress: 0,
        message: 'Uploading file to Azure Blob Storage...'
      });
      
      // Process the document
      const result = await processPdfDocument(file, (progress) => {
        if (progress < 25) {
          setUploadStatus({ 
            status: 'uploading', 
            progress, 
            message: 'Uploading file to Azure Blob Storage...'
          });
        } else if (progress < 75) {
          setUploadStatus({ 
            status: 'processing', 
            progress, 
            message: 'Processing document with Azure AI Document Intelligence...'
          });
        } else {
          setUploadStatus({ 
            status: 'processing', 
            progress, 
            message: 'Indexing extracted content in Azure AI Search...'
          });
        }
      });
      
      setProcessedDocument(result);
      setUploadStatus({ status: 'complete' });
      toast.success('Document processed and indexed successfully');
    } catch (error: any) {
      console.error('Error processing document:', error);
      setUploadStatus({ 
        status: 'error', 
        error: error.message || 'Failed to process document' 
      });
      toast.error('Failed to process document. Please try again.');
    }
  };

  const handleReset = () => {
    setProcessedDocument(null);
    setUploadStatus({ status: 'idle' });
  };

  const handleCancel = () => {
    setUploadStatus({ status: 'idle' });
    toast('Processing cancelled');
  };

  const renderUploadContent = () => {
    if (uploadStatus.status === 'uploading' || uploadStatus.status === 'processing') {
      return <ProcessingView status={uploadStatus} onCancel={handleCancel} />;
    }

    if (uploadStatus.status === 'complete' && processedDocument) {
      return <ResultView document={processedDocument} onReset={handleReset} />;
    }

    return (
      <div className="flex flex-col items-center max-w-4xl mx-auto">
        <div className="mb-10 text-center">
          <div className="inline-block mb-4">
            <div className="bg-primary/10 p-4 rounded-full">
              <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary animate-float">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                <polyline points="14 2 14 8 20 8" />
                <path d="M16 13H8" />
                <path d="M16 17H8" />
                <path d="M10 9H8" />
              </svg>
            </div>
          </div>
          <h1 className="text-3xl font-medium mb-3">Document Intelligence</h1>
          <p className="text-muted-foreground max-w-lg mx-auto text-balance">
            Extract paragraphs, tables, figures, and handwriting from your PDF documents 
            using Azure AI Document Intelligence.
          </p>
        </div>
        <FileUpload onFileSelected={handleFileSelected} />
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'upload' | 'search')}>
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
            <TabsTrigger value="upload">Upload & Process</TabsTrigger>
            <TabsTrigger value="search">Search Documents</TabsTrigger>
          </TabsList>
          <TabsContent value="upload" className="mt-0">
            {renderUploadContent()}
          </TabsContent>
          <TabsContent value="search" className="mt-0">
            <Search />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ icon, title, description }) => {
  return (
    <div className="bg-white/60 backdrop-blur-sm p-6 rounded-xl border border-border/50 hover:shadow-md transition-all duration-300 hover:-translate-y-1">
      <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
        <div className="text-primary">{icon}</div>
      </div>
      <h3 className="text-lg font-medium mb-2">{title}</h3>
      <p className="text-muted-foreground text-sm">{description}</p>
    </div>
  );
};

export default Index;
