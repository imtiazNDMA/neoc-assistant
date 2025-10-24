#!/usr/bin/env python3
"""
Quick test for NEOC AI Assistant components
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        from neoc_assistant.document_processor import document_processor

        print("Document processor imported successfully")

        from neoc_assistant.llm_service import llm_service

        print("LLM service imported successfully")

        from neoc_assistant.rag_pipeline import rag_pipeline

        print("RAG pipeline imported successfully")

        from neoc_assistant.routers import chat, documents

        print("Routers imported successfully")

        return True
    except Exception as e:
        print(f"Import error: {e}")
        return False


def test_vectorstore():
    """Test vectorstore functionality"""
    print("\nTesting vectorstore...")

    try:
        from neoc_assistant.document_processor import document_processor

        if document_processor.vectorstore:
            count = document_processor.vectorstore._collection.count()
            print(f"Vectorstore has {count} documents")

            # Test search
            docs = document_processor.search_similar("disaster", k=2)
            print(f"Search returned {len(docs)} results")
            return True
        else:
            print("Vectorstore not initialized")
            return False
    except Exception as e:
        print(f"Vectorstore error: {e}")
        return False


def test_llm():
    """Test LLM service"""
    print("\nTesting LLM service...")

    try:
        from neoc_assistant.llm_service import llm_service

        # Test status check
        status = llm_service.check_ollama_status()
        print(f"Ollama status: {status}")

        return True
    except Exception as e:
        print(f"LLM service error: {e}")
        return False


def main():
    """Run quick tests"""
    print("Quick Test of NEOC AI Assistant Components")
    print("=" * 40)

    results = []
    results.append(("Imports", test_imports()))
    results.append(("Vectorstore", test_vectorstore()))
    results.append(("LLM Service", test_llm()))

    print("\n" + "=" * 40)
    print("Results:")
    for test, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test}: {status}")

    all_pass = all(result for _, result in results)
    print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")


if __name__ == "__main__":
    main()
