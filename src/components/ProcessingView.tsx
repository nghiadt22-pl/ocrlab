
import React from 'react';
import { Progress } from '@/components/ui/progress';
import { Loader2Icon, ServerIcon, DatabaseIcon, AlertCircleIcon, FileTextIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { UploadStatus } from '@/lib/types';

interface ProcessingViewProps {
  status: UploadStatus;
  onCancel: () => void;
}

const ProcessingView: React.FC<ProcessingViewProps> = ({ status, onCancel }) => {
  const getStatusIcon = () => {
    if (status.status === 'error') {
      return <AlertCircleIcon className="h-8 w-8 text-destructive animate-pulse" />;
    } else if (status.status === 'uploading') {
      return <ServerIcon className="h-8 w-8 text-primary animate-pulse" />;
    } else if (status.message?.includes('Indexing')) {
      return <DatabaseIcon className="h-8 w-8 text-primary animate-pulse" />;
    } else if (status.message?.includes('Processing document')) {
      return <FileTextIcon className="h-8 w-8 text-primary animate-pulse" />;
    } else {
      return <Loader2Icon className="h-8 w-8 text-primary animate-spin" />;
    }
  };

  // Extract a cleaner error message from the full error string
  const getCleanErrorMessage = (errorMsg: string | undefined): string => {
    if (!errorMsg) return 'Unknown error occurred';
    
    // Check for specific error patterns
    if (errorMsg.includes('Network error') || errorMsg.includes('Failed to fetch')) {
      return 'Network connection error. The app is running in simulation mode since it cannot connect to Azure services.';
    }
    
    if (errorMsg.includes('Azure API error')) {
      return 'Azure service error. Please try again later. The app is running in simulation mode.';
    }
    
    if (errorMsg.includes('Azure Search API error')) {
      return 'Azure Search indexing error. The extraction will still work, but search functionality may be limited.';
    }
    
    if (errorMsg.includes('CORS')) {
      return 'Cross-origin resource sharing (CORS) error. This is an application configuration issue.';
    }
    
    // If no specific pattern matched, return a generic but helpful message
    return errorMsg.length > 100 ? `${errorMsg.substring(0, 100)}...` : errorMsg;
  };

  // Get a descriptive title based on the status
  const getStatusTitle = () => {
    if (status.status === 'error') {
      if (status.error?.includes('Failed to fetch') || status.error?.includes('Network error')) {
        return 'Network Connection Error';
      }
      return 'Processing Error';
    }
    
    if (status.status === 'uploading') {
      return 'Uploading to Azure Storage';
    }
    
    if (status.message?.includes('Indexing')) {
      return 'Indexing in Azure AI Search';
    }
    
    if (status.message?.includes('Processing document')) {
      return 'Processing with Azure AI';
    }
    
    return 'Processing Document';
  };

  return (
    <div className="w-full max-w-lg mx-auto bg-white/70 backdrop-blur-md rounded-xl p-8 shadow-sm border border-border/50 animate-fade-in">
      <div className="flex flex-col items-center text-center">
        <div className={`w-16 h-16 rounded-full ${status.status === 'error' ? 'bg-destructive/10' : 'bg-primary/10'} flex items-center justify-center mb-6`}>
          {getStatusIcon()}
        </div>
        
        <h3 className="text-xl font-medium mb-2">
          {getStatusTitle()}
        </h3>
        
        <p className={`${status.status === 'error' ? 'text-destructive' : 'text-muted-foreground'} mb-6 max-w-sm`}>
          {status.status === 'error' ? getCleanErrorMessage(status.error) : (status.message || 'Please wait while we process your document...')}
        </p>
        
        {status.status !== 'error' && status.progress !== undefined && (
          <div className="w-full mb-6">
            <Progress value={status.progress} className="h-2" />
            <p className="text-sm text-muted-foreground mt-2">
              {Math.round(status.progress)}% Complete
            </p>
          </div>
        )}
        
        <Button variant={status.status === 'error' ? 'default' : 'outline'} onClick={onCancel}>
          {status.status === 'error' ? 'Try Again' : 'Cancel'}
        </Button>
      </div>
    </div>
  );
};

export default ProcessingView;
