# SCL Health FAISS API Documentation

This repository now includes a RESTful API that allows external applications to access the document processing and Q&A functionality using token-based authentication.

## Getting Started

### 1. Setup API Token

Copy the example environment file and configure your API tokens:

```bash
cp .env.example .env
```

Edit `.env` file with your settings:
```bash
# API Configuration
API_TOKENS=your-secret-token-1,your-secret-token-2
OPENAI_API_KEY=your-openai-api-key

# Optional keys for enhanced functionality
GOOGLE_API_KEY=your-google-api-key
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API Server

```bash
python api_server.py
```

The API server will start on `http://localhost:8000`

## API Endpoints

### Authentication

All API endpoints (except `/health` and `/`) require a Bearer token in the Authorization header:

```bash
Authorization: Bearer your-api-token
```

### Available Endpoints

#### 1. Health Check
- **GET** `/health`
- Returns API status
- No authentication required

```bash
curl http://localhost:8000/health
```

#### 2. Root Information
- **GET** `/`
- Returns API information and available endpoints  
- No authentication required

```bash
curl http://localhost:8000/
```

#### 3. Upload PDF Document
- **POST** `/api/upload`
- Upload a PDF document for processing
- Optionally generates queries from the document

```bash
curl -X POST \
  -H "Authorization: Bearer your-api-token" \
  -F "file=@path/to/document.pdf" \
  -F "generate_queries=true" \
  http://localhost:8000/api/upload
```

**Response:**
```json
{
  "success": true,
  "message": "Document uploaded and processed successfully",
  "filename": "document.pdf",
  "queries": ["Question 1", "Question 2", "..."]
}
```

#### 4. List Documents
- **GET** `/api/documents`
- List all uploaded documents

```bash
curl -H "Authorization: Bearer your-api-token" \
  http://localhost:8000/api/documents
```

**Response:**
```json
{
  "documents": ["doc1.pdf", "doc2.pdf", "..."]
}
```

#### 5. Query Documents
- **POST** `/api/query`
- Query the FAISS database for answers
- Optionally cache Q&A pairs for faster future responses

```bash
curl -X POST \
  -H "Authorization: Bearer your-api-token" \
  -F "query=What is the main topic?" \
  -F "filename=document.pdf" \
  http://localhost:8000/api/query
```

**Response:**
```json
{
  "success": true,
  "answer": "The main topic is...",
  "source": "faiss_search"  // or "qa_store" for cached answers
}
```

#### 6. Generate Queries
- **POST** `/api/generate-queries`
- Generate new queries from an already uploaded document

```bash
curl -X POST \
  -H "Authorization: Bearer your-api-token" \
  -F "filename=document.pdf" \
  http://localhost:8000/api/generate-queries
```

**Response:**
```json
{
  "success": true,
  "queries": ["Generated question 1", "Generated question 2"],
  "query_file": "query/document.pdf_query.txt"
}
```

## Python Client Example

Use the provided Python client for easy integration:

```python
from api_client_example import SCLHealthAPIClient

# Initialize client
client = SCLHealthAPIClient(
    base_url="http://localhost:8000",
    api_token="your-api-token"
)

# Upload document
result = client.upload_document("path/to/document.pdf")
print(result)

# List documents
documents = client.list_documents()
print(documents)

# Query documents
answer = client.query_documents("What is this document about?")
print(answer)
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- **401**: Invalid or missing API token
- **400**: Bad request (e.g., invalid file type, empty query)
- **404**: Resource not found (e.g., document not found)
- **500**: Internal server error

Example error response:
```json
{
  "detail": "Invalid or missing API token"
}
```

## Running with Docker (Optional)

Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "api_server.py"]
```

Build and run:
```bash
docker build -t scl-health-api .
docker run -p 8000:8000 --env-file .env scl-health-api
```

## Security Notes

1. Keep your API tokens secure and rotate them regularly
2. Use HTTPS in production environments
3. Configure CORS settings appropriately for your use case
4. Consider rate limiting for production deployments
5. Store API tokens in environment variables, not in code

## Integration Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': 'Bearer your-api-token'
  }
});

// List documents
const documents = await client.get('/api/documents');
console.log(documents.data);

// Query
const formData = new FormData();
formData.append('query', 'What is machine learning?');
const answer = await client.post('/api/query', formData);
console.log(answer.data);
```

### curl Examples

See the endpoint documentation above for complete curl examples.

## Troubleshooting

1. **"Invalid or missing API token"**: Check that your token is correctly set in the Authorization header
2. **"OPENAI_API_KEY environment variable is required"**: Ensure your OpenAI API key is configured
3. **Connection refused**: Make sure the API server is running on the correct port
4. **Internal server errors**: Check the server logs for detailed error messages

## Support

For issues and questions, check the server logs and ensure all environment variables are properly configured.