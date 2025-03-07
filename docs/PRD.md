# Overview

OCR LAB is a web application that performs advanced OCR extraction on PDF documents (including tables, images, and handwritten text) and then stores the extracted data in a vector database for semantic search and retrieval-augmented generation. It includes file/folder management, usage monitoring, and a simple REST API for querying relevant document chunks and optional pay-as-you-go billing. 

Below is a concise breakdown of the requested information based on the product requirements:

---

## 1. User Flow (Step-by-Step)

1. **Sign Up / Login**  
   - User registers for an account (via Clerk).  
   - On the first login, a default “Home” folder is created, or the user can create custom folders.

2. **Create Folder & Upload PDFs**  
   - User clicks “Create Folder” to organize documents.  
   - User uploads one or multiple PDFs (up to 100MB per file).  
   - Files enter a processing queue.

3. **OCR & Metadata Extraction (Asynchronous)**  
   - A Python microservice retrieves PDFs from Azure Blob Storage, performs OCR (text, images, tables, handwriting) using Azure Document Intelligence.  
   - Generates document summaries, keywords, JSON metadata.  
   - All text chunks and metadata are stored in:
     - **Postgres** for file metadata and usage stats.  
     - **Vector DB** for semantic search (e.g., Azure AI Search).

4. **View & Search Extracted Data**  
   - Once OCR completes, the file status changes to “Complete.”  
   - Users can query the data via:  
     - A basic search bar in the front-end.  
     - A REST API with `POST {"query": "<question>", "n": 5}` for top-5 relevant chunks.

5. **Download & Delete**  
   - Users can download the original PDFs.  
   - Users can delete a file, which removes the PDF from Azure Blob Storage, its embeddings from the vector DB, and metadata from Postgres.

6. **Usage Tracking & Billing** (Optional, depending on user tier)  
   - The system logs pages processed and queries made.  
   - A usage dashboard displays these metrics, and pay-as-you-go billing is integrated (e.g., via HitPay).

---

## 2. Tech Stack & APIs

1. **Front-End:**  
   - **Vite** + shadcn/ui for a responsive, minimal user interface (folders, file upload, usage dashboard).

2. **Back-End Services:**  
   - **Azure Blob Storage** for PDF file storage.  
   - **Azure Queue** for asynchronous OCR processing.  
   - **Azure Functions (Python)** to handle:
     - OCR extraction (tables, images, handwriting) with Azure Document Intelligence.  
     - Summaries/keywords/metadata generation.  
     - Vector embeddings upsert to the vector database.
   - **Postgres (Azure Postgres)** for user management, file/folder metadata, usage stats.

3. **Vector Database:**  
   - **Azure AI Search** for storing embeddings of text chunks.

4. **REST API:**  
   - A minimal set of endpoints (e.g., `POST /api/query`, `GET /api/files`, etc.) for:  
     - **Semantic Search:** Given a query, returns top-n relevant text chunks and metadata.  
     - **User & File Management:** CRUD operations on folders/files.

5. **Optional Services:**  
   - **HitPay** for payment processing.  
   - **Sentry** for error logging and monitoring.

---

## 3. Core Features

1. **File & Folder Management**  
   - Users can create folders, upload PDFs (bulk uploads supported), organize documents.

2. **OCR Extraction (Advanced)**  
   - Extracts text, tables, images, and basic handwritten text.  
   - Uses Azure Document Intelligence as OCR services 

3. **Document Summaries & Metadata**  
   - Summaries and keywords for each file to improve search accuracy.  
   - Table/Image data included as text and JSON metadata.

4. **Vector Database Storage**  
   - Text chunks and metadata stored for **semantic search** and retrieval-augmented generation (RAG).

5. **Semantic Search & REST API**  
   - A simple REST endpoint for retrieving the most relevant chunks based on a natural language query.  
   - The front-end also provides a basic search bar.

6. **Usage Monitoring & Billing**  
   - Tracks pages processed and queries made.  
   - Supports pay-as-you-go or free tier pricing with HitPay integration.

7. **Compliance & Security**
   - API key authentication for external clients.

---

## 4. In-Scope vs. Out-of-Scope

**In-Scope**  
- **End-to-End OCR Pipeline** (including tables/images/handwriting).  
- **Document Summaries, Keywords, JSON Metadata.**  
- **Folder & File Management** (create/delete folders, upload/delete files).  
- **Storing and Indexing Extracted Data** in Postgres (metadata) + Vector DB (embeddings).  
- **Simple REST API** for semantic search queries (top-n chunks).  
- **Basic Dashboard** for usage (pages processed, queries made).  
- **Basic Billing Integration** (HitPay) and usage-based pricing.  

**Out-of-Scope**  
- **Extensive Document Editing** (e.g., rewriting or rearranging extracted text in the UI).  
- **Complex Role-Based Access Control** beyond basic user ownership (e.g., advanced ACLs for teams).  
- **Granular Analytics** or advanced analytics dashboards beyond showing usage metrics.  
- **Large-Scale Real-Time Processing** for high-throughput OCR (the aim is “quality over speed” with moderate throughput).  
- **Non-PDF Formats** (MVP is focused on PDFs; other file types are not prioritized initially).  
- **Heavy Customization of Summaries/Keywords** (the system auto-generates basic summaries but does not provide advanced customization or specialized domain-specific summarization out of the box).



