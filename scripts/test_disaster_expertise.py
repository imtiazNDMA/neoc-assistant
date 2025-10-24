#!/usr/bin/env python3
"""
Test Disaster Management Expertise
Validates that the NEOC AI Assistant has proper disaster management knowledge
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_disaster_types():
    """Test that the system has disaster management expertise"""
    disaster_keywords = [
        "disaster", "hazard", "natural", "emergency", "mitigation",
        "prevention", "response", "recovery", "prediction"
    ]

    print("[INFO] Testing disaster management expertise...")

    # Check the system prompt in LLM service
    from neoc_assistant.llm_service import LLMService

    llm_service = LLMService()
    system_prompt = str(llm_service.chat_prompt.template)
    found_keywords = []

    for keyword in disaster_keywords:
        if keyword.lower() in system_prompt.lower():
            found_keywords.append(keyword)

    coverage = len(found_keywords) / len(disaster_keywords)
    print(".1%")

    return {
        "total_keywords": len(disaster_keywords),
        "found_keywords": len(found_keywords),
        "coverage": coverage,
        "passed": coverage >= 0.7  # At least 70% coverage of disaster keywords
    }

def test_citation_requirements():
    """Test that citation requirements are properly configured"""
    print("[INFO] Testing citation requirements...")

    from neoc_assistant.llm_service import LLMService

    llm_service = LLMService()
    system_prompt = str(llm_service.chat_prompt.template)

    citation_indicators = [
        "ieee", "citation", "bibliography", "reference"
    ]

    found_indicators = []
    for indicator in citation_indicators:
        if indicator.lower() in system_prompt.lower():
            found_indicators.append(indicator)

    coverage = len(found_indicators) / len(citation_indicators)
    print(".1%")

    return {
        "citation_indicators": citation_indicators,
        "found_indicators": found_indicators,
        "coverage": coverage,
        "passed": coverage >= 0.8  # At least 80% of citation requirements present
    }

def test_rag_components():
    """Test that RAG components are properly initialized"""
    print("[INFO] Testing RAG components...")

    try:
        from neoc_assistant.rag_pipeline import RAGPipeline
        from neoc_assistant.document_processor import DocumentProcessor
        from neoc_assistant.llm_service import LLMService

        # Test component initialization
        rag = RAGPipeline()
        doc_processor = DocumentProcessor()
        llm_service = LLMService()

        return {
            "rag_initialized": True,
            "doc_processor_initialized": True,
            "llm_service_initialized": True,
            "passed": True
        }

    except Exception as e:
        print(f"[FAIL] RAG component initialization failed: {e}")
        return {
            "error": str(e),
            "passed": False
        }

def test_monitoring_setup():
    """Test that monitoring components are configured"""
    print("[INFO] Testing monitoring setup...")

    try:
        from neoc_assistant.monitoring import init_monitoring, get_system_metrics
        from neoc_assistant.security import init_security_manager
        from neoc_assistant.config import config

        # Test monitoring initialization
        init_monitoring()
        init_security_manager(config)

        metrics = get_system_metrics()

        return {
            "monitoring_initialized": True,
            "security_initialized": True,
            "metrics_available": bool(metrics),
            "passed": True
        }

    except Exception as e:
        print(f"[FAIL] Monitoring setup failed: {e}")
        return {
            "error": str(e),
            "passed": False
        }

def main():
    """Run all disaster expertise tests"""
    print("NEOC AI Assistant - Disaster Management Expertise Test")
    print("=" * 55)

    tests = [
        ("Disaster Types Recognition", test_disaster_types),
        ("Citation Requirements", test_citation_requirements),
        ("RAG Components", test_rag_components),
        ("Monitoring Setup", test_monitoring_setup)
    ]

    results = {}
    passed_tests = 0

    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 30)

        try:
            result = test_func()
            results[test_name] = result

            if result.get("passed", False):
                print(f"[PASS] {test_name} passed")
                passed_tests += 1
            else:
                print(f"[FAIL] {test_name} failed")

        except Exception as e:
            print(f"[ERROR] {test_name} crashed: {e}")
            results[test_name] = {"error": str(e), "passed": False}

    # Summary
    print("\n" + "=" * 55)
    print("TEST SUMMARY")
    print("=" * 55)

    total_tests = len(tests)
    success_rate = passed_tests / total_tests

    print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1%})")

    if success_rate >= 0.75:  # 75% success threshold
        print("[SUCCESS] Disaster management expertise validation PASSED")
        return 0
    else:
        print("[FAIL] Disaster management expertise validation FAILED")
        return 1

if __name__ == "__main__":
    exit(main())