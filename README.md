# Document Intelligence Application

A modern web application for extracting and indexing content from PDF documents using Azure AI Document Intelligence.

![Document Intelligence Application](public/og-image.png)

## Features

- **PDF Document Processing**: Extract text, tables, figures, and handwriting from PDF documents
- **Azure AI Integration**: Leverages Azure AI Document Intelligence for accurate content extraction
- **Search Indexing**: Indexes extracted content in Azure AI Search for future retrieval
- **User-Friendly Interface**: Modern, responsive UI built with React and Tailwind CSS
- **Resilient Design**: Fallback mechanisms for when cloud services are unavailable
- **CI/CD Pipeline**: Automated deployment using GitHub Actions

## Getting Started

### Prerequisites

- Node.js (v16 or later)
- npm, yarn, or bun package manager

### Installation

1. Clone the repository
2. Install dependencies:
```
npm install
```
3. Start the development server:
```
npm run dev
```

## Documentation

For more detailed information, check out these documentation files:

- [Architecture Overview](ARCHITECTURE.md)
- [Component Guide](COMPONENT_GUIDE.md)
- [API Integration Guide](API_INTEGRATION_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Contribution Guide](CONTRIBUTION_GUIDE.md)
- [Deployment Guide](.github/workflows/README.md)

## Usage

1. **Upload a PDF Document**: 
   - Drag and drop a PDF file into the upload area, or click to select a file
   - Maximum file size: 15MB

2. **Processing**:
   - The document is uploaded to Azure Blob Storage
   - Azure AI Document Intelligence extracts content
   - Extracted content is indexed in Azure AI Search

3. **View Results**:
   - View extracted paragraphs, tables, figures, and handwriting
   - Filter results by content type
   - Export results to JSON format

## Technologies Used

- **Frontend**: React, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: Azure Functions, Python
- **Cloud Services**: Azure Blob Storage, Azure AI Document Intelligence, Azure AI Search
- **Authentication**: Clerk
- **CI/CD**: GitHub Actions

## Deployment

### Backend Deployment

The Azure Functions backend is automatically deployed using GitHub Actions. Two workflow options are available:

1. **Azure Functions GitHub Action**: Uses the official Azure Functions GitHub Action
2. **Azure Functions CLI**: Uses the Azure Functions Core Tools CLI directly

For setup instructions and more details, see the [Deployment Guide](.github/workflows/README.md).

## Contributing

Contributions are welcome! Please see our [Contribution Guide](CONTRIBUTION_GUIDE.md) for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Lovable](https://lovable.dev)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- PDF processing powered by [Azure AI Document Intelligence](https://azure.microsoft.com/en-us/services/cognitive-services/document-intelligence/)
