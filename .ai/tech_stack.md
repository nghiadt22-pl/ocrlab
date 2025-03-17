Below is a detailed description of all the technical components that make up OCR Lab. This document covers the front-end, back-end, the services used (Azure Blob Storage, Azure Queue, Azure Document Intelligence, and others), the database (Postgres), the vector store (Azure AI Search), and optional integrations (Sentry, HitPay). You will also find a list of the main packages and dependencies required in both JavaScript and Python environments, along with links to relevant documentation. 

---

## 1. Overview

OCR Lab is structured as a web application with a React-based front-end (built using Vite) and a set of back-end services that handle file storage, OCR, vector indexing, and search. The front-end interacts with the back-end through a minimal REST API and uses Clerk for user management. The back-end leverages Azure services for file storage (Blob), queue processing (Queue), and advanced OCR (Azure Document Intelligence). It stores metadata in Postgres and embeddings in Azure AI Search (acting as the vector database).

---

## 2. Front-End

**Primary Technology:**
- **Vite** (with React) as the build tool and development server.
- **shadcn/ui** (React + Tailwind components) for a minimal, responsive UI.
- **Clerk** for sign-up and login flows.

**Core Dependencies (JavaScript/TypeScript):**
- `react` / `react-dom`: Core libraries for building UI.
- `@clerk/clerk-react`: Integration with Clerk authentication.
- `@tanstack/react-query` (optional but recommended): For data fetching and caching.
- `axios` or `fetch`: For making REST calls to the back-end.
- `shadcn/ui` (which relies on `tailwindcss`): For pre-built components and styling.
- `vite`: Build tool (dev server, bundling, etc.).
- `typescript`: If using TypeScript in the front-end codebase.

**Installation Example (Front-End):**
```bash
# Create a new Vite + React project (TypeScript example)
npm create vite@latest ocr-lab-frontend -- --template react-ts
cd ocr-lab-frontend

# Install key dependencies
npm install react react-dom @clerk/clerk-react @tanstack/react-query axios \
            tailwindcss postcss autoprefixer shadcn/ui

# Install dev tools
npm install -D typescript vite

# Initialize Tailwind (if needed)
npx tailwindcss init -p
```

**Documentation Links (Front-End):**
- [Vite Official Docs](https://vitejs.dev/guide/)
- [React Docs](https://react.dev/)
- [Clerk Docs](https://clerk.dev/docs)
- [shadcn/ui Reference](https://ui.shadcn.com/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)

---

## 3. Back-End Services

The back-end is composed of Python microservices and Azure Functions. These services handle OCR extraction, interaction with Azure Queue, Azure Blob Storage, and the vector database.

### 3.1 Python Environment

**Core Dependencies (Python):**
1. **Azure SDK Libraries** for interacting with Azure services:
   - `azure-storage-blob`: For uploading/downloading PDFs to/from Blob Storage.  
     - [Azure Blob Storage Docs](https://learn.microsoft.com/azure/storage/blobs/)
   - `azure-storage-queue`: For sending/receiving messages to the processing queue.  
     - [Azure Queue Storage Docs](https://learn.microsoft.com/azure/storage/queues/)
   - `azure-ai-formrecognizer`: For advanced OCR through Azure Document Intelligence (previously "Form Recognizer").  
     - [Azure Form Recognizer (Document Intelligence) Docs](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
2. **Database Libraries**:
   - `psycopg2` or `asyncpg`: For connecting to Postgres.
   - [PostgreSQL Docs](https://www.postgresql.org/docs/)
3. **Vector Database Integration**:
   - Depending on your approach, you can use `azure-search-documents` for Azure Cognitive Search:
     - [Azure Cognitive Search Docs](https://learn.microsoft.com/azure/search/)
   - If you wrap this with a vector index approach, you may also include additional libraries for chunking or embeddings if needed (e.g., `sentence-transformers`).
4. **Azure Functions** for building serverless REST endpoints.
   - [Azure Functions Python Docs](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
5. **Requests / httpx**: If needed for external HTTP requests, though Azure SDK often covers most Azure calls.

**Installation Example (Back-End):**
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install Azure libraries
pip install azure-storage-blob azure-storage-queue azure-ai-formrecognizer azure-search-documents

# Install database libraries
pip install psycopg2

# Install Azure Functions libraries
pip install azure-functions

# Example for advanced text processing or embedding generation
pip install sentence-transformers
```

**Azure Functions (Python)**
For serverless deployment with Azure Functions:
```bash
pip install azure-functions
```
- [Azure Functions Python Docs](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)

---

### 3.2 Azure Services Configuration

1. **Azure Blob Storage** is used to store the original PDF documents. You will need to create a Storage Account in Azure and configure your containers.  
   - [Azure Blob Storage Setup](https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-portal)

2. **Azure Queue** is used for asynchronous message passing between the front-end's upload notifications and the OCR processing microservice.  
   - [Azure Queue Storage Setup](https://learn.microsoft.com/azure/storage/queues/)

3. **Azure Document Intelligence (Form Recognizer)** is called by the Python service to extract text, tables, images, and handwriting from PDFs.  
   - [Getting Started with Form Recognizer](https://learn.microsoft.com/azure/ai-services/document-intelligence/get-started-form-recognizer?tabs=studio)

4. **Azure Cognitive Search (Vector Mode)** or **Azure AI Search** is used to store embeddings for semantic search and retrieval.  
   - [Azure Cognitive Search Docs](https://learn.microsoft.com/azure/search/)

---

## 4. Postgres Database

OCR Lab uses Postgres to store:
- User information and usage (if you're not relying entirely on Clerk for user data).
- File metadata and folder structures.
- Statistics on pages processed and queries made.

**Recommended Libraries:**
- `psycopg2` for synchronous usage.
- `asyncpg` if you prefer asynchronous access in Python.

A typical table structure might include a `files` table with columns for `id`, `folder_id`, `status`, `original_filename`, and so on, and a `folders` table with the user's folder structure.

[PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 5. REST API

OCR Lab exposes a minimal REST API using Azure Functions for external or internal front-end calls. Typical endpoints include:
- **File Management** (`GET /api/files`, `POST /api/files`, `DELETE /api/files/{id}`)
- **Folder Management** (`GET /api/folders`, `POST /api/folders`, `DELETE /api/folders/{id}`)
- **Query** (`POST /api/query`): Accepts a JSON object such as `{"query": "some question", "n": 5}` and returns the top relevant chunks.

Below are example links to reference materials for setting up REST APIs with Azure Functions:
- [Azure Functions HTTP Trigger Docs](https://learn.microsoft.com/azure/azure-functions/functions-bindings-http-webhook-trigger)
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)

**Sample Query Endpoint Body:**
```json
{
  "query": "What does the sales report say about Q4 results?",
  "n": 5
}
```

The response typically includes an array of text chunks and associated metadata, plus any additional information like the file name or folder name.

---

## 6. Optional Services

### 6.1 Sentry
For error logging and monitoring, you can integrate Sentry with both the front-end (React) and back-end (Python or Node).
- [Sentry Docs](https://docs.sentry.io/)

### 6.2 HitPay
For pay-as-you-go billing, OCR Lab can integrate with HitPay to handle payment processing and transaction tracking.
- [HitPay API Reference](https://hitpay.app/docs)

### 6.3 Clerk (Auth)
Although mentioned in the front-end section, Clerk can also be configured server-side for user/session management.
- [Clerk Docs](https://clerk.dev/docs)

---

## 7. Summary of Installation Steps

1. **Provision Azure Resources**  
   Create a Storage Account, enable Blob Storage and Queue, set up Azure Document Intelligence, and set up Azure AI Search.

2. **Set Up Postgres**  
   Spin up an Azure Database for PostgreSQL or a self-hosted Postgres. Configure environment variables.

3. **Configure Python Environment**  
   Install required Azure SDKs, database drivers, and any libraries for your OCR pipeline.

4. **Configure Node Environment (Front-End)**  
   Use Vite to set up the React project. Install dependencies like Clerk, Tailwind, and any additional libraries.

5. **Implement REST Endpoints with Azure Functions**  
   Set up Azure Functions for file/folder management and the search endpoint.

6. **Set Up Monitoring & Billing (Optional)**  
   Integrate Sentry for error logging and HitPay for billing flows, if needed.

---

## 8. Additional Links and Resources

- **Azure Portal**: [https://portal.azure.com/](https://portal.azure.com/)  
- **Azure CLI**: [https://learn.microsoft.com/cli/azure/](https://learn.microsoft.com/cli/azure/)  
- **Python Package Index (PyPI)**: [https://pypi.org/](https://pypi.org/)  
- **npm** (Node Package Manager): [https://www.npmjs.com/](https://www.npmjs.com/)  

Feel free to adjust these dependencies based on your specific implementation details. This list covers the core technologies needed for OCR Lab and points you to the official documentation for further configuration and deployment.