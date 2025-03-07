
import React, { useState } from 'react';
import { 
  FileTextIcon, 
  TableIcon, 
  ImageIcon, 
  PencilIcon, 
  CopyIcon, 
  CheckIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from 'lucide-react';
import { ExtractedItem } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { toast } from 'sonner';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

interface ExtractedContentProps {
  item: ExtractedItem;
}

const formatConfidence = (confidence: number): string => {
  return `${(confidence * 100).toFixed(0)}%`;
};

export const ExtractedContent: React.FC<ExtractedContentProps> = ({ item }) => {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const handleCopy = () => {
    let textToCopy = '';
    
    if (item.type === 'paragraph' || item.type === 'handwriting') {
      textToCopy = item.content as string;
    } else if (item.type === 'table') {
      const table = item.content as string[][];
      textToCopy = table.map(row => row.join('\t')).join('\n');
    } else {
      textToCopy = 'Image content cannot be copied as text.';
    }
    
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    toast.success('Content copied to clipboard');
    
    setTimeout(() => {
      setCopied(false);
    }, 2000);
  };

  const getIcon = () => {
    switch (item.type) {
      case 'paragraph':
        return <FileTextIcon className="h-4 w-4" />;
      case 'table':
        return <TableIcon className="h-4 w-4" />;
      case 'figure':
        return <ImageIcon className="h-4 w-4" />;
      case 'handwriting':
        return <PencilIcon className="h-4 w-4" />;
      default:
        return <FileTextIcon className="h-4 w-4" />;
    }
  };

  const getTitle = () => {
    switch (item.type) {
      case 'paragraph':
        return 'Paragraph';
      case 'table':
        return 'Table';
      case 'figure':
        return 'Figure';
      case 'handwriting':
        return 'Handwriting';
      default:
        return 'Content';
    }
  };

  const renderContent = () => {
    switch (item.type) {
      case 'paragraph':
      case 'handwriting':
        const text = item.content as string;
        return (
          <div className={cn(
            "text-sm", 
            !expanded && text.length > 200 ? "line-clamp-3" : "",
            item.type === 'handwriting' ? "font-medium italic" : ""
          )}>
            {text}
          </div>
        );
      
      case 'table':
        const table = item.content as string[][];
        return (
          <div className="overflow-x-auto max-w-full">
            <table className="min-w-full border-collapse text-sm">
              <thead>
                <tr className="bg-muted">
                  {table[0]?.map((cell, i) => (
                    <th key={i} className="border border-border/60 px-3 py-2 text-left font-medium">
                      {cell}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {table.slice(1).map((row, i) => (
                  <tr key={i} className="even:bg-muted/30">
                    {row.map((cell, j) => (
                      <td key={j} className="border border-border/60 px-3 py-2">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      
      case 'figure':
        return (
          <div className="w-full flex justify-center">
            <div className="relative rounded-md overflow-hidden max-w-full border border-border">
              <img 
                src={item.content as string} 
                alt="Extracted figure" 
                className="max-h-64 object-contain"
              />
            </div>
          </div>
        );
      
      default:
        return <div>Unknown content type</div>;
    }
  };

  const needsExpand = 
    (item.type === 'paragraph' || item.type === 'handwriting') && 
    (item.content as string).length > 200;

  return (
    <Card className="w-full overflow-hidden transition-all duration-300 hover:shadow-md bg-white/90 backdrop-blur-sm animate-scale-in">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="bg-primary/10 p-1.5 rounded">
              {getIcon()}
            </div>
            <h3 className="font-medium">{getTitle()}</h3>
            <Badge variant="outline" className="ml-2 text-xs">
              Page {item.pageNumber}
            </Badge>
          </div>
          <Badge variant="secondary" className="text-xs">
            Confidence: {formatConfidence(item.confidence)}
          </Badge>
        </div>
      </CardHeader>
      <Separator />
      <CardContent className="pt-4">
        {renderContent()}
      </CardContent>
      <CardFooter className="flex justify-between pt-2 pb-3">
        <div>
          {needsExpand && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setExpanded(!expanded)}
              className="text-xs h-8 px-2"
            >
              {expanded ? (
                <>
                  <ChevronUpIcon className="h-3 w-3 mr-1" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDownIcon className="h-3 w-3 mr-1" />
                  Show more
                </>
              )}
            </Button>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          className="text-xs h-8"
          onClick={handleCopy}
          disabled={item.type === 'figure'}
        >
          {copied ? (
            <>
              <CheckIcon className="h-3 w-3 mr-1" />
              Copied
            </>
          ) : (
            <>
              <CopyIcon className="h-3 w-3 mr-1" />
              Copy
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  );
};
