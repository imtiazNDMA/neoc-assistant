#!/usr/bin/env python3
"""
Functionality Test Script for NEOC AI Assistant
Tests disaster management expertise and citation functionality
"""

import json
import time
from typing import Dict, List

import requests


class FunctionalityTester:
    """Test disaster management functionality and citations"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def test_chat_functionality(self) -> Dict:
        """Test chat functionality with disaster management queries"""
        print("[INFO] Testing chat functionality...")

        test_queries = [
            "What are the main types of natural disasters?",
            "How should communities prepare for earthquakes?",
            "Explain flood risk assessment methods",
            "What are the phases of disaster management?",
            "How does climate change affect disaster frequency?",
        ]

        results = {}
        for i, query in enumerate(test_queries):
            try:
                print(f"[INFO] Testing query {i+1}: {query[:50]}...")
                response = requests.post(
                    f"{self.base_url}/api/chat/", json={"message": query}, timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    results[f"query_{i+1}"] = {
                        "success": True,
                        "response_length": len(data.get("response", "")),
                        "has_citations": "bibliography"
                        in data.get("response", "").lower()
                        or "references" in data.get("response", "").lower(),
                        "response_time": response.elapsed.total_seconds(),
                    }
                else:
                    results[f"query_{i+1}"] = {
                        "success": False,
                        "error": f"Status code: {response.status_code}",
                    }

            except Exception as e:
                results[f"query_{i+1}"] = {"success": False, "error": str(e)}

        return results

    def test_health_endpoint(self) -> Dict:
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_tests(self) -> Dict:
        """Run all functionality tests"""
        print("Testing NEOC AI Assistant Functionality")
        print("=" * 40)

        results = {}

        # Test health
        print("[INFO] Testing health endpoint...")
        results["health"] = self.test_health_endpoint()

        if not results["health"]["success"]:
            print("[FAIL] Health check failed - cannot proceed with other tests")
            return results

        # Test chat functionality
        results["chat"] = self.test_chat_functionality()

        # Analyze results
        chat_results = results["chat"]
        successful_queries = sum(1 for r in chat_results.values() if r["success"])
        citation_queries = sum(
            1 for r in chat_results.values() if r.get("has_citations", False)
        )

        results["summary"] = {
            "total_queries": len(chat_results),
            "successful_queries": successful_queries,
            "citation_coverage": (
                citation_queries / len(chat_results) if chat_results else 0
            ),
            "overall_success": results["health"]["success"] and successful_queries > 0,
        }

        return results

    def print_report(self, results: Dict):
        """Print test report"""
        print("\nTest Results Summary")
        print("=" * 40)

        if results["health"]["success"]:
            print("[PASS] Health check passed")
        else:
            print("[FAIL] Health check failed")
            return

        summary = results["summary"]
        print(
            f"[INFO] Chat queries: {summary['successful_queries']}/{summary['total_queries']} successful"
        )
        print(".1%")

        if summary["overall_success"]:
            print("[PASS] Overall functionality test PASSED")
        else:
            print("[FAIL] Overall functionality test FAILED")

        print("\nDetailed Results:")
        for query_id, result in results["chat"].items():
            status = "[PASS]" if result["success"] else "[FAIL]"
            citations = " (with citations)" if result.get("has_citations") else ""
            print(
                f"  {status} {query_id}: {result.get('response_length', 0)} chars{citations}"
            )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="NEOC AI Assistant Functionality Test")
    parser.add_argument(
        "--url", default="http://localhost:8000", help="Base URL of the service"
    )

    args = parser.parse_args()

    tester = FunctionalityTester(args.url)
    results = tester.run_tests()
    tester.print_report(results)

    return 0 if results.get("summary", {}).get("overall_success", False) else 1


if __name__ == "__main__":
    exit(main())
