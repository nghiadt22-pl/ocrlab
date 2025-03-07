export type ContentType = 'paragraph' | 'table' | 'figure' | 'handwriting';

export interface ExtractedItem {
  id: string;
  type: ContentType;
  content: string | string[][] | string; // Text for paragraphs/handwriting, 2D array for tables, base64 for figures
  confidence: number;
  pageNumber: number;
  boundingBox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface ProcessedDocument {
  id: string;
  filename: string;
  extractedContent: ExtractedItem[];
  processedAt: Date;
}

export interface UploadStatus {
  status: 'idle' | 'uploading' | 'processing' | 'complete' | 'error';
  progress?: number;
  message?: string;
  error?: string;
}

export interface SearchResult {
  id: string;
  content: string;
  content_vector?: number[];  // Optional since it might not be returned in search results
  metadata: string;
}

export interface SearchRequest {
  query?: string;
  vector?: number[];
  select?: string[];
}

export interface SearchResponse {
  value: SearchResult[];
}

export interface SearchState {
  status: 'idle' | 'loading' | 'success' | 'error';
  results: SearchResult[];
  error?: string;
}
