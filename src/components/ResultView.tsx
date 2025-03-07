
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { 
  FileTextIcon, 
  TableIcon, 
  ImageIcon, 
  PencilIcon, 
  DownloadIcon,
  RefreshCwIcon,
  CheckCircleIcon
} from 'lucide-react';
import { ExtractedContent } from './ExtractedContent';
import { ProcessedDocument, ContentType } from '@/lib/types';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';

interface ResultViewProps {
  document: ProcessedDocument;
  onReset: () => void;
}

const ResultView: React.FC<ResultViewProps> = ({ document, onReset }) => {
  const [activeTab, setActiveTab] = useState<ContentType | 'all'>('all');
  
  const filteredContent = document.extractedContent.filter(item => 
    activeTab === 'all' || item.type === activeTab
  );

  const contentCounts = {
    paragraph: document.extractedContent.filter(item => item.type === 'paragraph').length,
    table: document.extractedContent.filter(item => item.type === 'table').length,
    figure: document.extractedContent.filter(item => item.type === 'figure').length,
    handwriting: document.extractedContent.filter(item => item.type === 'handwriting').length,
  };

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(document, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${document.filename.replace('.pdf', '')}_extracted.json`;
    
    // Fix: Use window.document instead of document to avoid name collision
    const linkElement = window.document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    toast.success('JSON file downloaded');
  };

  return (
    <div className="w-full max-w-4xl mx-auto animate-fade-in">
      <div className="bg-white/80 backdrop-blur-md rounded-xl p-6 shadow-sm border border-border/50 mb-8">
        <div className="flex items-center mb-4">
          <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center mr-3">
            <CheckCircleIcon className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-medium">Document Processed Successfully</h2>
            <p className="text-sm text-muted-foreground">{document.filename}</p>
          </div>
        </div>

        <Separator className="my-4" />
        
        <Tabs defaultValue="all" value={activeTab} onValueChange={(v) => setActiveTab(v as ContentType | 'all')}>
          <div className="flex items-center justify-between mb-4">
            <TabsList>
              <TabsTrigger value="all" className="flex items-center gap-1">
                All
                <span className="ml-1 text-xs bg-muted rounded-full px-2 py-0.5">
                  {document.extractedContent.length}
                </span>
              </TabsTrigger>
              <TabsTrigger value="paragraph" className="flex items-center gap-1">
                <FileTextIcon className="h-3.5 w-3.5 mr-1" />
                Paragraphs
                <span className="ml-1 text-xs bg-muted rounded-full px-2 py-0.5">
                  {contentCounts.paragraph}
                </span>
              </TabsTrigger>
              <TabsTrigger value="table" className="flex items-center gap-1">
                <TableIcon className="h-3.5 w-3.5 mr-1" />
                Tables
                <span className="ml-1 text-xs bg-muted rounded-full px-2 py-0.5">
                  {contentCounts.table}
                </span>
              </TabsTrigger>
              <TabsTrigger value="figure" className="flex items-center gap-1">
                <ImageIcon className="h-3.5 w-3.5 mr-1" />
                Figures
                <span className="ml-1 text-xs bg-muted rounded-full px-2 py-0.5">
                  {contentCounts.figure}
                </span>
              </TabsTrigger>
              <TabsTrigger value="handwriting" className="flex items-center gap-1">
                <PencilIcon className="h-3.5 w-3.5 mr-1" />
                Handwriting
                <span className="ml-1 text-xs bg-muted rounded-full px-2 py-0.5">
                  {contentCounts.handwriting}
                </span>
              </TabsTrigger>
            </TabsList>

            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleExportJSON}>
                <DownloadIcon className="h-4 w-4 mr-2" />
                Export JSON
              </Button>
              <Button variant="outline" size="sm" onClick={onReset}>
                <RefreshCwIcon className="h-4 w-4 mr-2" />
                Process Another
              </Button>
            </div>
          </div>

          <TabsContent value="all" className="mt-0">
            <div className="space-y-4">
              {filteredContent.map(item => (
                <ExtractedContent key={item.id} item={item} />
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="paragraph" className="mt-0">
            <div className="space-y-4">
              {filteredContent.map(item => (
                <ExtractedContent key={item.id} item={item} />
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="table" className="mt-0">
            <div className="space-y-4">
              {filteredContent.map(item => (
                <ExtractedContent key={item.id} item={item} />
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="figure" className="mt-0">
            <div className="space-y-4">
              {filteredContent.map(item => (
                <ExtractedContent key={item.id} item={item} />
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="handwriting" className="mt-0">
            <div className="space-y-4">
              {filteredContent.map(item => (
                <ExtractedContent key={item.id} item={item} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ResultView;
