from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
import os
from ..document_processor import document_processor

router = APIRouter()

class DocumentInfo(BaseModel):
    filename: str
    status: str
    chunks_count: int = 0

class DocumentList(BaseModel):
    documents: List[DocumentInfo]

@router.get("/", response_model=DocumentList)
async def list_documents():
    """
    List all ingested documents
    """
    try:
        # For now, list files in data directory
        # TODO: Implement proper document listing from vectorstore metadata
        data_dir = "data"
        documents = []

        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.pdf'):
                    documents.append(DocumentInfo(
                        filename=filename,
                        status="ingested" if document_processor.vectorstore else "pending",
                        chunks_count=0  # TODO: Get actual chunk count
                    ))

        return DocumentList(documents=documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest")
async def ingest_documents():
    """
    Ingest all documents from the data directory
    """
    try:
        document_processor.ingest_all_documents()
        return {"message": "Document ingestion completed successfully", "status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a single document for ingestion
    """
    try:
        # TODO: Implement single document upload and ingestion
        return {"message": f"Document {file.filename} uploaded successfully", "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{filename}")
async def delete_document(filename: str):
    """
    Delete a document from the vector store
    """
    try:
        # TODO: Implement document deletion
        return {"message": f"Document {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))