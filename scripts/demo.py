#!/usr/bin/env python3
"""
Demo script for NEOC AI Assistant
Shows how to use the disaster management LLM application programmatically
"""

from rag_pipeline import rag_pipeline

def demo_chat():
    """Demonstrate the chatbot functionality"""
    print("NEOC AI Assistant Demo")
    print("=" * 50)
    print("Asking questions about comprehensive disaster management...")
    print()

    questions = [
        "What are the main types of natural hazards and their characteristics?",
        "How can communities prepare for multiple hazard scenarios?",
        "What are the most effective early warning systems for earthquakes?",
        "How do mitigation strategies differ between floods and hurricanes?",
        "What role does AI play in disaster risk reduction?",
        "Explain the effectiveness of tsunami early warning systems"
    ]

    for question in questions:
        print(f"Q: {question}")
        try:
            result = rag_pipeline.process_query(question)
            print(f"A: {result['response'][:200]}...")
            if result['sources']:
                print(f"Sources: {', '.join(result['sources'])}")
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()

def demo_ui_instructions():
    """Show instructions for using the web UI"""
    print("Web UI Instructions:")
    print("=" * 50)
    print("1. Start the server:")
    print("   uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload")
    print()
    print("2. Open your browser and go to:")
    print("   http://localhost:8000")
    print()
    print("3. Start chatting with the AI assistant!")
    print()
    print("Features:")
    print("- Clean, minimal interface")
    print("- Real-time responses")
    print("- Source citations")
    print("- Conversation memory")
    print("- Responsive design")

if __name__ == "__main__":
    demo_chat()
    print()
    demo_ui_instructions()