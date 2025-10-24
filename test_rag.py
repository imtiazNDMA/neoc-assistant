import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from neoc_assistant.rag_pipeline import rag_pipeline

try:
    print("Testing RAG pipeline...")
    response = rag_pipeline.process_query("Hello", "test_conv")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()