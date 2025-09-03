"""
FastAPI server providing token-based API access to SCL Health FAISS functionality.
Allows external applications to upload documents, generate queries, and perform Q&A.
"""

import os
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
import io

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query as QueryParam, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing modules
from modules.pdf_reader import parse_pdf, generate_question_with_genai, create_query_file, load_pdf, add_qa_file, check_qafile_exist
from modules.faissdb import store_pdf_documents
from modules.query_handler import query_faiss_db
from doc_handler import check_file_exist
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure OpenAI API key is available
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY not found. Please set it in your .env file or environment variables.")
    print("The API will not function properly without this key.")

# Initialize FastAPI app
app = FastAPI(
    title="SCL Health FAISS API",
    description="API for document processing, query generation, and Q&A using FAISS vector search",
    version="1.0.0"
)

# Add CORS middleware for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security setup
security = HTTPBearer()

# Configuration for API tokens
API_TOKENS = os.getenv("API_TOKENS", "").split(",") if os.getenv("API_TOKENS") else []
DEFAULT_TOKEN = os.getenv("DEFAULT_API_TOKEN", "scl-health-api-token-2024")

# Add default token if no tokens configured
if not API_TOKENS:
    API_TOKENS = [DEFAULT_TOKEN]

# Response models
class UploadResponse(BaseModel):
    success: bool
    message: str
    filename: str
    queries: Optional[List[str]] = None

class DocumentsResponse(BaseModel):
    documents: List[str]

class QueryResponse(BaseModel):
    success: bool
    answer: str
    source: str  # "qa_store" or "faiss_search"

class GenerateQueriesResponse(BaseModel):
    success: bool
    queries: List[str]
    query_file: str

class ErrorResponse(BaseModel):
    error: str
    detail: str

# Authentication
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token"""
    if not credentials.credentials or credentials.credentials not in API_TOKENS:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or missing API token"
        )
    return credentials.credentials

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "SCL Health FAISS API",
        "version": "1.0.0",
        "description": "API for document processing and Q&A using FAISS vector search",
        "endpoints": {
            "upload": "POST /api/upload - Upload PDF documents",
            "documents": "GET /api/documents - List uploaded documents", 
            "query": "POST /api/query - Query the FAISS database",
            "generate-queries": "POST /api/generate-queries - Generate queries from document"
        }
    }

@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    generate_queries: bool = QueryParam(True, description="Generate queries from the uploaded document"),
    token: str = Depends(verify_token)
):
    """Upload a PDF document and optionally generate queries"""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Check if file already exists
        if check_file_exist("uploaded", file.filename):
            return UploadResponse(
                success=False,
                message=f"{file.filename} already exists",
                filename=file.filename
            )
        
        # Save uploaded file
        uploaded_path = f"uploaded/{file.filename}"
        content = await file.read()
        
        with open(uploaded_path, "wb") as f:
            f.write(content)
        
        # Parse PDF and load into FAISS
        file_obj = io.BytesIO(content)
        file_obj.name = file.filename  # Add name attribute for compatibility
        
        text = parse_pdf(file_obj)
        documents = load_pdf(uploaded_path)
        
        # Store in FAISS database
        result = store_pdf_documents(documents)
        
        queries = None
        if generate_queries:
            # Generate queries using GenAI
            queries = generate_question_with_genai(text)
            create_query_file(file.filename, queries)
        
        return UploadResponse(
            success=True,
            message="Document uploaded and processed successfully",
            filename=file.filename,
            queries=queries
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/api/documents", response_model=DocumentsResponse)
async def list_documents(token: str = Depends(verify_token)):
    """List all uploaded documents"""
    try:
        uploaded_files = os.listdir("uploaded") if os.path.exists("uploaded") else []
        return DocumentsResponse(documents=uploaded_files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(
    query: str = Form(..., description="Query text"),
    filename: Optional[str] = Form(None, description="Optional filename for Q&A caching"),
    token: str = Depends(verify_token)
):
    """Query the FAISS database or existing Q&A pairs"""
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # First check if we have a cached Q&A pair
        if filename:
            qa_response = check_qafile_exist(filename, query)
            if qa_response:
                return QueryResponse(
                    success=True,
                    answer=qa_response["answer"],
                    source="qa_store"
                )
        
        # If no cached answer, query FAISS database
        response = query_faiss_db(query)
        
        if not response:
            raise HTTPException(status_code=404, detail="No relevant documents found")
        
        # Save Q&A pair if filename provided
        if filename:
            qa_pair = {"query": query, "answer": response.content}
            add_qa_file(filename, qa_pair)
        
        return QueryResponse(
            success=True,
            answer=response.content,
            source="faiss_search"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/api/generate-queries", response_model=GenerateQueriesResponse)
async def generate_queries_from_document(
    filename: str = Form(..., description="Filename of uploaded document"),
    token: str = Depends(verify_token)
):
    """Generate queries from an already uploaded document"""
    
    uploaded_path = f"uploaded/{filename}"
    
    if not os.path.exists(uploaded_path):
        raise HTTPException(status_code=404, detail=f"Document {filename} not found")
    
    try:
        # Load and parse the document
        documents = load_pdf(uploaded_path)
        
        # Read the document content for query generation
        with open(uploaded_path, "rb") as f:
            content = f.read()
            file_obj = io.BytesIO(content)
            file_obj.name = filename
            text = parse_pdf(file_obj)
        
        # Generate queries
        queries = generate_question_with_genai(text)
        query_file = create_query_file(filename, queries)
        
        return GenerateQueriesResponse(
            success=True,
            queries=queries,
            query_file=query_file
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating queries: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "scl-health-faiss-api"}

if __name__ == "__main__":
    import uvicorn
    
    # Ensure required directories exist
    os.makedirs("uploaded", exist_ok=True)
    os.makedirs("query", exist_ok=True)
    os.makedirs("qa_pair", exist_ok=True)
    
    print("Starting SCL Health FAISS API Server...")
    print(f"API Tokens configured: {len(API_TOKENS)}")
    print("Available endpoints:")
    print("  POST /api/upload - Upload PDF documents")
    print("  GET /api/documents - List uploaded documents")
    print("  POST /api/query - Query the FAISS database") 
    print("  POST /api/generate-queries - Generate queries from document")
    print("  GET /health - Health check")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)