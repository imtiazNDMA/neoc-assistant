#!/usr/bin/env python3
"""
Test script for the NEOC AI Assistant chatbot
"""

from neoc_assistant.rag_pipeline import rag_pipeline
from neoc_assistant.routers.documents import router as docs_router
import json

def test_document_ingestion():
    """Test document ingestion"""
    print("Testing document ingestion...")
    from neoc_assistant.document_processor import document_processor

    try:
        # Check if vectorstore exists
        if document_processor.vectorstore:
            count = document_processor.vectorstore._collection.count()
            print(f"Vectorstore loaded with {count} documents")
        else:
            print("Vectorstore not initialized")
    except Exception as e:
        print(f"Error checking vectorstore: {e}")

def test_rag_pipeline():
    """Test RAG pipeline with sample queries"""
    print("\nTesting RAG pipeline...")

    test_queries = [
        "What is disaster prediction?",
        "How does air pollution modeling work?",
        "What are the challenges in environmental monitoring?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = rag_pipeline.process_query(query)
            print(f"Response: {result['response'][:200]}...")
            print(f"Sources: {result['sources']}")
            print("Query processed successfully")
        except Exception as e:
            print(f"Error processing query: {e}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    # Note: This would require the server to be running
    print("API testing requires server to be running. Skipping for now.")

def main():
    """Run all tests"""
    print("Testing NEOC AI Assistant Chatbot")
    print("=" * 50)

    test_document_ingestion()
    test_rag_pipeline()
    test_api_endpoints()

    print("\n" + "=" * 50)
    print("Testing completed!")

if __name__ == "__main__":
    main()