# Documents API

The Documents API provides endpoints for managing document collections, uploading files, and performing document-based operations for the RAG (Retrieval-Augmented Generation) system.

## Base URL

```
http://localhost:8000/api/documents
```

## Endpoints

### GET /api/documents/

List all documents in the collection.

#### Request

```http
GET /api/documents/
```

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Maximum documents to return (default: 50) |
| `offset` | integer | No | Number of documents to skip (default: 0) |
| `search` | string | No | Search query for filtering documents |
| `category` | string | No | Filter by document category |
| `date_from` | string | No | Filter documents from date (ISO 8601) |
| `date_to` | string | No | Filter documents to date (ISO 8601) |

#### Response

```json
{
  "documents": [
    {
      "id": "doc_001",
      "filename": "earthquake_preparedness.pdf",
      "title": "Earthquake Preparedness Guide",
      "category": "preparedness",
      "file_size": 2457600,
      "mime_type": "application/pdf",
      "upload_date": "2024-01-15T10:30:00Z",
      "last_modified": "2024-01-15T10:30:00Z",
      "chunk_count": 45,
      "status": "processed",
      "metadata": {
        "author": "USGS",
        "pages": 25,
        "language": "en"
      }
    }
  ],
  "total_count": 1,
  "has_more": false,
  "processing_stats": {
    "total_documents": 150,
    "processed_documents": 148,
    "failed_documents": 2,
    "total_chunks": 12500
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `documents` | array | Array of document objects |
| `total_count` | integer | Total number of documents matching query |
| `has_more` | boolean | Whether more results are available |
| `processing_stats` | object | Overall collection statistics |

#### Document Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique document identifier |
| `filename` | string | Original filename |
| `title` | string | Document title (extracted or provided) |
| `category` | string | Document category |
| `file_size` | integer | File size in bytes |
| `mime_type` | string | MIME type |
| `upload_date` | string | Upload timestamp (ISO 8601) |
| `last_modified` | string | Last modification timestamp |
| `chunk_count` | integer | Number of text chunks |
| `status` | string | Processing status |
| `metadata` | object | Additional metadata |

### POST /api/documents/upload

Upload one or more documents to the collection.

#### Request

```http
POST /api/documents/upload
Content-Type: multipart/form-data
```

Form data:
- `files`: One or more files (PDF, TXT, MD, etc.)
- `category`: Optional category for all files
- `metadata`: Optional JSON metadata

#### cURL Example

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer your-api-key" \
  -F "files=@earthquake_guide.pdf" \
  -F "files=@flood_preparedness.txt" \
  -F "category=preparedness" \
  -F 'metadata={"source": "USGS", "year": 2023}'
```

#### Response

```json
{
  "uploaded": [
    {
      "id": "doc_002",
      "filename": "earthquake_guide.pdf",
      "status": "processing",
      "estimated_completion": "2024-01-15T10:31:00Z"
    },
    {
      "id": "doc_003",
      "filename": "flood_preparedness.txt",
      "status": "processing",
      "estimated_completion": "2024-01-15T10:30:30Z"
    }
  ],
  "failed": [],
  "batch_id": "batch_123456"
}
```

#### Supported File Types

| Format | MIME Type | Max Size | Notes |
|--------|-----------|----------|-------|
| PDF | application/pdf | 50MB | Text extraction supported |
| Text | text/plain | 10MB | UTF-8 encoding required |
| Markdown | text/markdown | 10MB | GitHub-flavored markdown |
| HTML | text/html | 10MB | Clean HTML preferred |
| CSV | text/csv | 25MB | Structured data |
| JSON | application/json | 25MB | Document collections |

### GET /api/documents/{document_id}

Retrieve detailed information about a specific document.

#### Request

```http
GET /api/documents/doc_001
```

#### Response

```json
{
  "id": "doc_001",
  "filename": "earthquake_preparedness.pdf",
  "title": "Earthquake Preparedness Guide",
  "category": "preparedness",
  "file_size": 2457600,
  "mime_type": "application/pdf",
  "upload_date": "2024-01-15T10:30:00Z",
  "last_modified": "2024-01-15T10:30:00Z",
  "chunk_count": 45,
  "status": "processed",
  "processing_log": [
    {
      "timestamp": "2024-01-15T10:30:05Z",
      "level": "INFO",
      "message": "Text extraction started"
    },
    {
      "timestamp": "2024-01-15T10:30:15Z",
      "level": "INFO",
      "message": "Text extraction completed: 45 chunks"
    },
    {
      "timestamp": "2024-01-15T10:30:20Z",
      "level": "INFO",
      "message": "Embeddings generated"
    }
  ],
  "metadata": {
    "author": "USGS",
    "pages": 25,
    "language": "en",
    "word_count": 12500
  },
  "chunks": [
    {
      "id": "chunk_001",
      "content": "Earthquake preparedness involves understanding seismic risks...",
      "page": 1,
      "position": 0
    }
  ]
}
```

### DELETE /api/documents/{document_id}

Delete a document from the collection.

#### Request

```http
DELETE /api/documents/doc_001
```

#### Response

```json
{
  "deleted": true,
  "document_id": "doc_001",
  "chunks_removed": 45,
  "vectors_removed": 45
}
```

### POST /api/documents/ingest

Trigger document ingestion for pending uploads.

#### Request

```http
POST /api/documents/ingest
Content-Type: application/json

{
  "document_ids": ["doc_002", "doc_003"],
  "force_reprocess": false,
  "priority": "normal"
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_ids` | array | No | Specific documents to process (default: all pending) |
| `force_reprocess` | boolean | No | Reprocess already processed documents |
| `priority` | string | No | Processing priority: "low", "normal", "high" |

#### Response

```json
{
  "ingestion_id": "ingest_789",
  "queued_documents": 2,
  "estimated_duration": 120,
  "status": "queued"
}
```

### GET /api/documents/ingest/{ingestion_id}

Check the status of a document ingestion job.

#### Request

```http
GET /api/documents/ingest/ingest_789
```

#### Response

```json
{
  "ingestion_id": "ingest_789",
  "status": "processing",
  "progress": {
    "completed": 1,
    "total": 2,
    "percentage": 50.0
  },
  "current_document": "doc_003",
  "start_time": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T10:32:00Z",
  "results": {
    "successful": 1,
    "failed": 0
  }
}
```

## Document Processing

### Processing Pipeline

1. **Upload Validation**: File type, size, and content checks
2. **Text Extraction**: Extract readable text from documents
3. **Chunking**: Split text into semantically meaningful chunks
4. **Embedding Generation**: Create vector embeddings for chunks
5. **Indexing**: Store chunks and vectors in vector database
6. **Metadata Storage**: Store document metadata and processing info

### Chunking Strategy

```python
# Example chunking configuration
CHUNKING_CONFIG = {
    "strategy": "semantic",  # semantic, fixed_size, paragraph
    "size": 512,             # tokens per chunk
    "overlap": 64,           # token overlap between chunks
    "separators": ["\n\n", "\n", ". ", " ", ""]
}
```

### Quality Assurance

- **Text Quality**: Minimum text length, language detection
- **Embedding Quality**: Vector normalization, outlier detection
- **Index Quality**: Similarity search validation, recall testing

## Search and Retrieval

### Document Search

```http
GET /api/documents/search?q=earthquake+preparedness&limit=10
```

#### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query |
| `limit` | integer | Maximum results |
| `threshold` | float | Similarity threshold (0.0-1.0) |
| `category` | string | Filter by category |
| `date_from` | string | Date range filter |

#### Search Response

```json
{
  "query": "earthquake preparedness",
  "results": [
    {
      "document_id": "doc_001",
      "chunk_id": "chunk_005",
      "content": "Earthquake preparedness involves creating emergency plans...",
      "similarity_score": 0.92,
      "metadata": {
        "page": 3,
        "position": 245
      }
    }
  ],
  "total_results": 1,
  "search_time": 0.15
}
```

## Batch Operations

### Bulk Upload

```python
import requests

files = [
    ('files', open('doc1.pdf', 'rb')),
    ('files', open('doc2.txt', 'rb')),
]

response = requests.post(
    "http://localhost:8000/api/documents/upload",
    files=files,
    data={'category': 'preparedness'}
)
```

### Bulk Delete

```python
document_ids = ['doc_001', 'doc_002', 'doc_003']

response = requests.post(
    "http://localhost:8000/api/documents/batch-delete",
    json={'document_ids': document_ids}
)
```

## Error Handling

### Common Errors

**File Upload Errors**
```json
{
  "error": "FileTooLargeError",
  "detail": "File size 75MB exceeds maximum 50MB",
  "document_id": null
}
```

**Processing Errors**
```json
{
  "error": "TextExtractionError",
  "detail": "Failed to extract text from PDF",
  "document_id": "doc_001"
}
```

**Validation Errors**
```json
{
  "error": "InvalidFileTypeError",
  "detail": "File type 'application/exe' not supported",
  "supported_types": ["application/pdf", "text/plain", "text/markdown"]
}
```

## Monitoring

### Document Statistics

```http
GET /api/documents/stats
```

```json
{
  "total_documents": 150,
  "total_size": 1073741824,  // 1GB
  "categories": {
    "preparedness": 45,
    "response": 38,
    "recovery": 32,
    "mitigation": 35
  },
  "processing_status": {
    "processed": 148,
    "processing": 2,
    "failed": 0
  },
  "storage_usage": {
    "vector_store": 524288000,  // 500MB
    "file_storage": 536870912   // 512MB
  }
}
```

### Performance Metrics

- `documents_upload_total`: Total uploads
- `documents_processing_time_seconds`: Processing duration
- `documents_search_time_seconds`: Search performance
- `documents_storage_bytes`: Storage usage

## Best Practices

### Upload Optimization

1. **Batch uploads** for multiple files
2. **Compress files** before upload (where appropriate)
3. **Validate locally** before upload
4. **Use appropriate categories** for organization

### Processing Optimization

1. **Monitor processing status** for large uploads
2. **Process during off-peak hours** for large batches
3. **Check processing logs** for failures
4. **Reprocess failed documents** after fixing issues

### Search Optimization

1. **Use specific queries** for better results
2. **Filter by category** when possible
3. **Adjust similarity threshold** based on needs
4. **Cache frequent searches** in application layer

## Security Considerations

### File Validation

- **Type checking**: Only allowed file types
- **Size limits**: Prevent resource exhaustion
- **Content scanning**: Malware detection
- **Metadata sanitization**: Remove sensitive information

### Access Control

- **Authentication**: API key required
- **Authorization**: User permissions
- **Audit logging**: All document operations logged
- **Data encryption**: Files encrypted at rest

## Examples

### Complete Upload and Processing Workflow

```python
import requests
import time

# 1. Upload document
with open('disaster_guide.pdf', 'rb') as f:
    response = requests.post(
        "http://localhost:8000/api/documents/upload",
        files={'files': f},
        data={'category': 'preparedness'},
        headers={'Authorization': 'Bearer your-api-key'}
    )

upload_data = response.json()
document_id = upload_data['uploaded'][0]['id']

# 2. Wait for processing
while True:
    status_response = requests.get(f"http://localhost:8000/api/documents/{document_id}")
    status = status_response.json()['status']

    if status == 'processed':
        break
    elif status == 'failed':
        raise Exception("Document processing failed")

    time.sleep(5)

# 3. Search document content
search_response = requests.get(
    "http://localhost:8000/api/documents/search",
    params={'q': 'earthquake safety', 'limit': 5}
)

results = search_response.json()
print(f"Found {len(results['results'])} relevant sections")
```

### Bulk Document Management

```python
import requests
from pathlib import Path

# Upload all PDFs in directory
pdf_dir = Path('./documents')
upload_files = []

for pdf_file in pdf_dir.glob('*.pdf'):
    upload_files.append(('files', open(pdf_file, 'rb')))

if upload_files:
    response = requests.post(
        "http://localhost:8000/api/documents/upload",
        files=upload_files,
        data={'category': 'reference'}
    )

    # Close all file handles
    for _, file_handle in upload_files:
        file_handle.close()

    print(f"Uploaded {len(upload_files)} documents")
```

## Support

For Documents API support:

- **API Documentation**: https://neoc-ai-assistant.readthedocs.io/api/documents.html
- **Issues**: https://github.com/your-org/neoc-ai-assistant/issues
- **Discussions**: https://github.com/your-org/neoc-ai-assistant/discussions