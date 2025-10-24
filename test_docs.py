import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from neoc_assistant.document_processor import document_processor

try:
    print("Testing document processor...")
    docs = document_processor.search_similar("Hello", k=2)
    print(f"Found {len(docs)} documents")
    for doc in docs:
        print(f"Doc: {doc.page_content[:100]}...")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()