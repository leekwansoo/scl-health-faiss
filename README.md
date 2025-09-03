Open AI 를 이용하여 Upload된 건강생활 잡지 PDF File 에서부터 Query 를 추출하고 Query file 과 Query-Answer pair file 로 webzine Reader Service를 제공함

## API Access for External Applications

This repository now includes a RESTful API (`api_server.py`) that allows external applications to access the document processing and Q&A functionality using token-based authentication.

### Quick Start - API Server

1. **Configure API Token**: Copy `.env.example` to `.env` and set your API tokens and OpenAI key
2. **Start API Server**: `python api_server.py`
3. **Access API**: Server runs on `http://localhost:8000`

### API Endpoints

- **POST** `/api/upload` - Upload PDF documents
- **GET** `/api/documents` - List uploaded documents  
- **POST** `/api/query` - Query the FAISS database
- **POST** `/api/generate-queries` - Generate queries from documents
- **GET** `/health` - Health check

### Example Usage

```bash
# List documents
curl -H "Authorization: Bearer your-api-token" http://localhost:8000/api/documents

# Upload document
curl -X POST -H "Authorization: Bearer your-api-token" \
     -F "file=@document.pdf" http://localhost:8000/api/upload

# Query documents
curl -X POST -H "Authorization: Bearer your-api-token" \
     -F "query=What is the main topic?" http://localhost:8000/api/query
```

See `API_DOCUMENTATION.md` for complete documentation and `api_client_example.py` for Python integration examples.

## Application Components

app.py:  Streamlit Entry
mainapp.py:  Webzine Service Main Flow 
  Functions: Main Menu
    OpenAI Credential Entry
    Upload PDF File
    Query From Uploaded File

modules.pdf_reader.py: Handle PDF file
  Functions:
    parse_pdf: Read the pdf and parse inti pages
    generate_query: generate queries from uploaded PDF File with LLM
    create_query_file: create query_file list of queries
    create_qa_file: create a file with list of question_answer pair for each query_file
    add_to_qa_file: add a qa_pair into a corresponding qa_file

modules.faiss_db.py: Handling of Faiss db
  Functions:
     store-vector data-into faiss_db
     similarty_search

