"""
Example client demonstrating how to use the SCL Health FAISS API
"""

import requests
import json
from pathlib import Path

class SCLHealthAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token or "scl-health-api-token-2024"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def upload_document(self, file_path: str, generate_queries: bool = True):
        """Upload a PDF document to the API"""
        url = f"{self.base_url}/api/upload"
        
        # Remove content-type for file upload
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/pdf')}
            params = {'generate_queries': generate_queries}
            response = requests.post(url, files=files, headers=headers, params=params)
        
        return response.json()
    
    def list_documents(self):
        """List all uploaded documents"""
        url = f"{self.base_url}/api/documents"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def query_documents(self, query: str, filename: str = None):
        """Query the FAISS database"""
        url = f"{self.base_url}/api/query"
        data = {"query": query}
        if filename:
            data["filename"] = filename
        
        # Use form data for this endpoint
        headers = {"Authorization": f"Bearer {self.api_token}"}
        response = requests.post(url, data=data, headers=headers)
        return response.json()
    
    def generate_queries(self, filename: str):
        """Generate queries from an uploaded document"""
        url = f"{self.base_url}/api/generate-queries"
        data = {"filename": filename}
        
        headers = {"Authorization": f"Bearer {self.api_token}"}
        response = requests.post(url, data=data, headers=headers)
        return response.json()
    
    def health_check(self):
        """Check API health"""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        return response.json()

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = SCLHealthAPIClient(
        base_url="http://localhost:8000",
        api_token="scl-health-api-token-2024"
    )
    
    print("SCL Health FAISS API Client Example")
    print("=" * 40)
    
    # Health check
    print("1. Health Check:")
    try:
        health = client.health_check()
        print(f"   Status: {health}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # List documents
    print("\n2. List Documents:")
    try:
        docs = client.list_documents()
        print(f"   Documents: {docs}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example PDF upload (uncomment and provide a real PDF file path)
    # print("\n3. Upload Document:")
    # try:
    #     result = client.upload_document("path/to/your/document.pdf")
    #     print(f"   Upload result: {result}")
    # except Exception as e:
    #     print(f"   Error: {e}")
    
    # Example query (uncomment after uploading a document)
    # print("\n4. Query Documents:")
    # try:
    #     result = client.query_documents("What is the main topic of this document?")
    #     print(f"   Query result: {result}")
    # except Exception as e:
    #     print(f"   Error: {e}")
    
    print("\nExample completed. Check API server logs for details.")