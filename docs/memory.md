# Project Rules and Guidelines

## Azure Search Index Management

1. **NEVER create or modify Azure Search indexes through code**
   - All index management must be done through Azure Portal or Infrastructure as Code
   - Index schema: testpl_index_6
   ```
   Fields:
   - id (String): Key field, Retrievable, Filterable
   - content (String): Retrievable, Searchable with standard analyzer
   - content_vector (SingleCollection): Searchable, Dimension: 1536
   - metadata (String): Retrievable, Searchable with standard analyzer
   ```

2. **Index Operations**
   - Only perform read and write operations against the existing index
   - Validate documents match the schema before indexing
   - Handle errors gracefully if index is not found or schema mismatch occurs

3. **Vector Search Configuration**
   - Vector dimension must be exactly 1536
   - Use "default" vector search configuration
   - Vector search is optional, fall back to text search when vector is not provided

4. **Error Handling**
   - Log index-related errors with detailed messages
   - Return user-friendly error messages
   - Never expose internal index details in error messages

## Development Guidelines

1. **Search Operations**
   - Use proper field selection in search queries
   - Implement pagination for search results
   - Handle both text and vector search appropriately
   - Validate search inputs before sending to Azure

2. **Document Indexing**
   - Validate document structure matches index schema
   - Properly format metadata as JSON string
   - Handle content vector when available
   - Implement proper error handling for indexing operations 