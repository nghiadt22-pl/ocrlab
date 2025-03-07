import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  SearchIcon, 
  FileTextIcon, 
  FolderIcon, 
  CalendarIcon, 
  BookOpenIcon,
  Loader2Icon,
  XIcon,
  ArrowUpRightIcon,
  FilterIcon,
  SlidersHorizontalIcon
} from 'lucide-react';
import Header from '@/components/Header';
import { toast } from 'sonner';
import { searchDocuments } from '@/lib/azure-search';
import { SearchResult } from '@/lib/types';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuCheckboxItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel
} from '@/components/ui/dropdown-menu';
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';

// Mock data for search results
const mockSearchResults: SearchResult[] = [
  {
    id: '1',
    content: 'The quarterly financial report shows a 15% increase in revenue compared to the previous quarter. This growth is primarily attributed to the expansion of our product line and increased market penetration in the Asia-Pacific region.',
    metadata: JSON.stringify({
      filename: 'Q1 Financial Report.pdf',
      processedAt: new Date('2023-02-15').toISOString(),
      blobUrl: '#',
      folderId: '2',
      folderName: 'Financial Reports',
      pageNumber: 3
    })
  },
  {
    id: '2',
    content: 'Employee handbook section 4.2: All employees are entitled to 20 days of paid vacation per year, which accrue at a rate of 1.67 days per month. Unused vacation days can be carried over to the next calendar year, up to a maximum of 10 days.',
    metadata: JSON.stringify({
      filename: 'Employee Handbook.pdf',
      processedAt: new Date('2023-02-20').toISOString(),
      blobUrl: '#',
      folderId: '1',
      folderName: 'Home',
      pageNumber: 12
    })
  },
  {
    id: '3',
    content: 'The project proposal outlines a 6-month development timeline with key milestones at months 2, 4, and 6. The estimated budget is $120,000, which includes development costs, testing, and deployment.',
    metadata: JSON.stringify({
      filename: 'Project Proposal.pdf',
      processedAt: new Date('2023-03-05').toISOString(),
      blobUrl: '#',
      folderId: '3',
      folderName: 'Contracts',
      pageNumber: 5
    })
  },
  {
    id: '4',
    content: 'Meeting minutes from March 10th: The team discussed the upcoming product launch and assigned responsibilities. Marketing will prepare promotional materials by April 1st, and the development team will finalize the product by March 25th.',
    metadata: JSON.stringify({
      filename: 'Meeting Minutes.pdf',
      processedAt: new Date('2023-03-10').toISOString(),
      blobUrl: '#',
      folderId: '4',
      folderName: 'Meeting Notes',
      pageNumber: 1
    })
  },
  {
    id: '5',
    content: 'The sales presentation highlights our competitive advantages: 1) Proprietary technology, 2) 24/7 customer support, 3) Flexible pricing models, and 4) Seamless integration with existing systems.',
    metadata: JSON.stringify({
      filename: 'Sales Presentation.pdf',
      processedAt: new Date('2023-03-15').toISOString(),
      blobUrl: '#',
      folderId: '2',
      folderName: 'Financial Reports',
      pageNumber: 8
    })
  }
];

// Mock folders for filtering
const mockFolders = [
  { id: '1', name: 'Home' },
  { id: '2', name: 'Financial Reports' },
  { id: '3', name: 'Contracts' },
  { id: '4', name: 'Meeting Notes' }
];

interface ParsedMetadata {
  filename: string;
  processedAt: string;
  blobUrl: string;
  folderId: string;
  folderName: string;
  pageNumber: number;
}

type SearchState = 'idle' | 'loading' | 'success' | 'error';

const Search: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  
  const [query, setQuery] = useState(initialQuery);
  const [searchState, setSearchState] = useState<SearchState>('idle');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [activeTab, setActiveTab] = useState<string>('all');
  const [isFilterDrawerOpen, setIsFilterDrawerOpen] = useState(false);
  
  // Filter states
  const [selectedFolders, setSelectedFolders] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<string>('any');
  const [sortBy, setSortBy] = useState<string>('relevance');

  useEffect(() => {
    if (initialQuery) {
      performSearch(initialQuery);
    }
  }, [initialQuery]);

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSearchState('idle');
      setResults([]);
      return;
    }

    try {
      setSearchState('loading');
      
      // In a real app, we would call the API
      // const results = await searchDocuments({ query: searchQuery });
      
      // For now, use mock data and filter based on the query
      const filteredResults = mockSearchResults.filter(result => 
        result.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        JSON.parse(result.metadata).filename.toLowerCase().includes(searchQuery.toLowerCase())
      );
      
      // Simulate API delay
      setTimeout(() => {
        setResults(filteredResults);
        setSearchState('success');
        
        // Update URL with search query
        setSearchParams({ q: searchQuery });
      }, 800);
    } catch (error) {
      console.error('Search error:', error);
      setSearchState('error');
      toast.error('Failed to search documents');
    }
  };

  const handleSearch = () => {
    performSearch(query);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const clearSearch = () => {
    setQuery('');
    setSearchState('idle');
    setResults([]);
    setSearchParams({});
  };

  const parseMetadata = (metadataStr: string): ParsedMetadata => {
    try {
      return JSON.parse(metadataStr);
    } catch {
      return {
        filename: 'Unknown file',
        processedAt: new Date().toISOString(),
        blobUrl: '#',
        folderId: '',
        folderName: 'Unknown folder',
        pageNumber: 1
      };
    }
  };

  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return 'Unknown date';
    }
  };

  const getFilteredResults = () => {
    if (results.length === 0) return [];
    
    let filtered = [...results];
    
    // Filter by folder
    if (selectedFolders.length > 0) {
      filtered = filtered.filter(result => {
        const metadata = parseMetadata(result.metadata);
        return selectedFolders.includes(metadata.folderId);
      });
    }
    
    // Filter by date range
    if (dateRange !== 'any') {
      const now = new Date();
      let cutoffDate = new Date();
      
      switch (dateRange) {
        case 'today':
          cutoffDate.setDate(now.getDate() - 1);
          break;
        case 'week':
          cutoffDate.setDate(now.getDate() - 7);
          break;
        case 'month':
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        case 'year':
          cutoffDate.setFullYear(now.getFullYear() - 1);
          break;
      }
      
      filtered = filtered.filter(result => {
        const metadata = parseMetadata(result.metadata);
        const processedDate = new Date(metadata.processedAt);
        return processedDate >= cutoffDate;
      });
    }
    
    // Sort results
    if (sortBy === 'date') {
      filtered.sort((a, b) => {
        const dateA = new Date(parseMetadata(a.metadata).processedAt);
        const dateB = new Date(parseMetadata(b.metadata).processedAt);
        return dateB.getTime() - dateA.getTime(); // Newest first
      });
    }
    // For 'relevance', we keep the original order (assuming the API returns results sorted by relevance)
    
    return filtered;
  };

  const filteredResults = getFilteredResults();
  const hasActiveFilters = selectedFolders.length > 0 || dateRange !== 'any';

  const renderSearchResults = () => {
    if (searchState === 'loading') {
      return (
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2Icon className="h-10 w-10 text-primary animate-spin mb-4" />
          <p className="text-muted-foreground">Searching documents...</p>
        </div>
      );
    }

    if (searchState === 'error') {
      return (
        <div className="flex flex-col items-center justify-center py-16 text-destructive">
          <p>An error occurred while searching. Please try again.</p>
        </div>
      );
    }

    if (searchState === 'success' && filteredResults.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-16">
          <BookOpenIcon className="h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No results found for "{query}"</p>
          {hasActiveFilters && (
            <p className="text-sm text-muted-foreground mt-2">Try removing some filters</p>
          )}
        </div>
      );
    }

    if (searchState === 'idle') {
      return (
        <div className="flex flex-col items-center justify-center py-16">
          <SearchIcon className="h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">Enter a search term to find documents</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Found {filteredResults.length} result{filteredResults.length !== 1 ? 's' : ''} for "{query}"
        </p>
        
        {filteredResults.map((result) => {
          const metadata = parseMetadata(result.metadata);
          
          return (
            <Card key={result.id} className="overflow-hidden">
              <CardContent className="p-4">
                <div className="flex items-start gap-3 mb-3">
                  <div className="bg-primary/10 p-2 rounded-md flex-shrink-0">
                    <FileTextIcon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium truncate">{metadata.filename}</h3>
                      <Button variant="ghost" size="sm" className="ml-2 h-8" asChild>
                        <a href={metadata.blobUrl} target="_blank" rel="noopener noreferrer">
                          <ArrowUpRightIcon className="h-4 w-4 mr-1" />
                          View
                        </a>
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mt-1">
                      <div className="flex items-center">
                        <FolderIcon className="h-3.5 w-3.5 mr-1" />
                        <span>{metadata.folderName}</span>
                      </div>
                      <div className="flex items-center">
                        <CalendarIcon className="h-3.5 w-3.5 mr-1" />
                        <span>{formatDate(metadata.processedAt)}</span>
                      </div>
                      <div className="flex items-center">
                        <BookOpenIcon className="h-3.5 w-3.5 mr-1" />
                        <span>Page {metadata.pageNumber}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <p className="text-sm">
                  {result.content}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">Search Documents</h1>
          
          <div className="flex gap-2 mb-6">
            <div className="relative flex-1">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search across all your documents..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                className="pl-10 pr-10"
              />
              {query && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 h-7 w-7"
                  onClick={clearSearch}
                >
                  <XIcon className="h-4 w-4" />
                </Button>
              )}
            </div>
            <Button onClick={handleSearch}>Search</Button>
            
            <Drawer open={isFilterDrawerOpen} onOpenChange={setIsFilterDrawerOpen}>
              <DrawerTrigger asChild>
                <Button variant="outline" className="gap-2 relative">
                  <SlidersHorizontalIcon className="h-4 w-4" />
                  Filters
                  {hasActiveFilters && (
                    <Badge variant="secondary" className="h-5 min-w-5 p-0 flex items-center justify-center absolute -top-2 -right-2">
                      {selectedFolders.length + (dateRange !== 'any' ? 1 : 0)}
                    </Badge>
                  )}
                </Button>
              </DrawerTrigger>
              <DrawerContent>
                <div className="mx-auto w-full max-w-sm">
                  <DrawerHeader>
                    <DrawerTitle>Search Filters</DrawerTitle>
                    <DrawerDescription>
                      Refine your search results with these filters
                    </DrawerDescription>
                  </DrawerHeader>
                  <div className="p-4 space-y-6">
                    <div>
                      <h4 className="text-sm font-medium mb-3">Folders</h4>
                      <div className="space-y-2">
                        {mockFolders.map(folder => (
                          <div key={folder.id} className="flex items-center space-x-2">
                            <Checkbox 
                              id={`folder-${folder.id}`} 
                              checked={selectedFolders.includes(folder.id)}
                              onCheckedChange={(checked) => {
                                if (checked) {
                                  setSelectedFolders([...selectedFolders, folder.id]);
                                } else {
                                  setSelectedFolders(selectedFolders.filter(id => id !== folder.id));
                                }
                              }}
                            />
                            <Label htmlFor={`folder-${folder.id}`}>{folder.name}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium mb-3">Date Range</h4>
                      <Select value={dateRange} onValueChange={setDateRange}>
                        <SelectTrigger>
                          <SelectValue placeholder="Any time" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="any">Any time</SelectItem>
                          <SelectItem value="today">Today</SelectItem>
                          <SelectItem value="week">Past week</SelectItem>
                          <SelectItem value="month">Past month</SelectItem>
                          <SelectItem value="year">Past year</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium mb-3">Sort By</h4>
                      <Select value={sortBy} onValueChange={setSortBy}>
                        <SelectTrigger>
                          <SelectValue placeholder="Relevance" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="relevance">Relevance</SelectItem>
                          <SelectItem value="date">Date (newest first)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <DrawerFooter>
                    <Button onClick={() => {
                      if (searchState === 'success') {
                        // Re-filter results
                        getFilteredResults();
                      }
                      setIsFilterDrawerOpen(false);
                    }}>
                      Apply Filters
                    </Button>
                    <DrawerClose asChild>
                      <Button variant="outline">Cancel</Button>
                    </DrawerClose>
                  </DrawerFooter>
                </div>
              </DrawerContent>
            </Drawer>
          </div>
          
          <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
            <TabsList>
              <TabsTrigger value="all">All Results</TabsTrigger>
              <TabsTrigger value="documents">Documents</TabsTrigger>
              <TabsTrigger value="tables">Tables</TabsTrigger>
              <TabsTrigger value="images">Images</TabsTrigger>
            </TabsList>
          </Tabs>
          
          {renderSearchResults()}
        </div>
      </main>
    </div>
  );
};

export default Search; 