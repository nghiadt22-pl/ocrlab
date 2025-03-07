import React, { useState, useCallback } from 'react';
import { SearchIcon, Loader2Icon, FileIcon, CalendarIcon, LinkIcon } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';
import { searchDocuments } from '@/lib/azure-search';
import { SearchState, SearchResult, SearchRequest } from '@/lib/types';
import { cn } from '@/lib/utils';
import debounce from 'lodash/debounce';

interface SearchProps {
  className?: string;
  vectorSearch?: boolean;
}

interface ParsedMetadata {
  filename: string;
  processedAt: string;
  blobUrl: string;
}

const Search: React.FC<SearchProps> = ({ className, vectorSearch = false }) => {
  const [query, setQuery] = useState('');
  const [searchState, setSearchState] = useState<SearchState>({
    status: 'idle',
    results: []
  });

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSearchState({ status: 'idle', results: [] });
      return;
    }

    try {
      setSearchState(prev => ({ ...prev, status: 'loading' }));

      const searchRequest: SearchRequest = {
        query: searchQuery,
        select: ['id', 'content', 'metadata']
      };

      const results = await searchDocuments(searchRequest);
      setSearchState({
        status: 'success',
        results
      });
    } catch (error) {
      console.error('Search error:', error);
      setSearchState({
        status: 'error',
        results: [],
        error: error instanceof Error ? error.message : 'An error occurred while searching'
      });
      toast.error('Failed to search documents');
    }
  };

  // Debounce search to avoid too many API calls
  const debouncedSearch = useCallback(
    debounce((value: string) => performSearch(value), 300),
    []
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
  };

  const parseMetadata = (metadataStr: string): ParsedMetadata | null => {
    try {
      return JSON.parse(metadataStr);
    } catch {
      return null;
    }
  };

  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString();
    } catch {
      return dateStr;
    }
  };

  const renderResults = () => {
    if (searchState.status === 'loading') {
      return (
        <div className="flex items-center justify-center py-8">
          <Loader2Icon className="h-6 w-6 animate-spin text-primary" />
        </div>
      );
    }

    if (searchState.status === 'error') {
      return (
        <div className="text-center py-8 text-destructive">
          <p>{searchState.error || 'An error occurred while searching'}</p>
        </div>
      );
    }

    if (searchState.results.length === 0 && query.trim()) {
      return (
        <div className="text-center py-8 text-muted-foreground">
          <p>No results found</p>
        </div>
      );
    }

    return searchState.results.map((result: SearchResult) => {
      const metadata = parseMetadata(result.metadata);

      return (
        <Card key={result.id} className="mb-4">
          <CardContent className="p-4">
            {metadata && (
              <div className="flex flex-wrap gap-4 mb-3 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <FileIcon className="h-4 w-4" />
                  <span>{metadata.filename}</span>
                </div>
                <div className="flex items-center gap-1">
                  <CalendarIcon className="h-4 w-4" />
                  <span>{formatDate(metadata.processedAt)}</span>
                </div>
                {metadata.blobUrl && (
                  <a 
                    href={metadata.blobUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 hover:text-foreground transition-colors"
                  >
                    <LinkIcon className="h-4 w-4" />
                    <span>View Original</span>
                  </a>
                )}
              </div>
            )}
            <p className="text-sm">{result.content}</p>
          </CardContent>
        </Card>
      );
    });
  };

  return (
    <div className={cn("w-full max-w-3xl mx-auto", className)}>
      <div className="relative mb-6">
        <Input
          type="text"
          placeholder={vectorSearch ? "Enter text for semantic search..." : "Search documents..."}
          value={query}
          onChange={handleInputChange}
          className="pl-10"
        />
        <SearchIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
      </div>

      <div className="space-y-4">
        {renderResults()}
      </div>
    </div>
  );
};

export default Search; 