import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from neoc_assistant.llm_service import llm_service

try:
    print("Testing LLM service...")
    response = llm_service.generate_response("Hello")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()