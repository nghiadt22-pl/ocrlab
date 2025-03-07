
# Component Guide

This document provides an overview of the main components in the Document Intelligence application.

## Page Components

### Index Page (`src/pages/Index.tsx`)

The main landing page of the application containing:
- Header component
- File upload interface
- Processing status display
- Results view for extracted content
- Feature cards explaining the capabilities

### Sign In Page (`src/pages/SignIn.tsx`)

Authentication page for user sign-in using Clerk authentication.

### Sign Up Page (`src/pages/SignUp.tsx`)

Registration page for new users using Clerk authentication.

## Core Feature Components

### FileUpload (`src/components/FileUpload.tsx`)

Handles PDF file selection through drag-and-drop or file browser. Validates file type (PDF only) and size (max 15MB).

**Key functionality:**
- File drag & drop handling
- File validation (type and size)
- Upload initiation

### ProcessingView (`src/components/ProcessingView.tsx`)

Displays the current status of document processing with:
- Visual progress indication
- Status messages
- Process cancellation option
- Error handling with user-friendly messages

The component adapts its display based on the current processing phase:
- Uploading to Azure Storage
- Processing with Azure AI
- Indexing in Azure Search
- Error states with specific messages

### ResultView (`src/components/ResultView.tsx`)

Displays the extracted content from processed documents:
- Tabbed interface for different content types
- Filtering options for paragraphs, tables, figures, and handwriting
- JSON export functionality
- Option to process another document

### ExtractedContent (`src/components/ExtractedContent.tsx`)

Renders different types of extracted content:
- Text paragraphs
- Tables with preserved structure
- Images and figures
- Handwritten text

## Utility Components

### Header (`src/components/Header.tsx`)

Application header with:
- Logo and title
- Navigation links
- User authentication controls

### UI Components

The application uses shadcn/ui components for consistent styling:
- Buttons
- Progress indicators
- Tabs
- Cards
- Form controls
