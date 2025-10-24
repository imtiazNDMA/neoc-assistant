"""
Integration tests for the complete NEOC AI Assistant disaster management system
"""

import time
from unittest.mock import patch

import pytest
import requests


class TestSystemIntegration:
    """Test complete system integration"""

    def test_full_pipeline_integration(self):
        """Test complete RAG pipeline from query to response"""
        from neoc_assistant.document_processor import document_processor
        from neoc_assistant.rag_pipeline import rag_pipeline

        # Mock document search
        with patch(
            "src.neoc_assistant.document_processor.document_processor.search_similar"
        ) as mock_search:
            mock_search.return_value = [
                type(
                    "MockDoc",
                    (),
                    {
                        "page_content": "Climate change affects weather patterns significantly.",
                        "metadata": {"source": "climate.pdf"},
                    },
                )()
            ]

            # Mock LLM response
            with patch(
                "src.neoc_assistant.rag_pipeline.rag_pipeline.llm_service.llm.invoke"
            ) as mock_llm:
                mock_llm.return_value = (
                    "Climate change affects weather patterns according to research."
                )

                # Test full pipeline
                start_time = time.time()
                result = rag_pipeline.process_query(
                    "How does climate change affect weather?", "test_conversation"
                )
                total_time = time.time() - start_time

                assert result["success"] is True
                assert "climate" in result["response"].lower()
                assert result["conversation_id"] == "test_conversation"
                assert isinstance(result["sources"], list)

                # Should complete within reasonable time
                assert total_time < 5.0  # 5 seconds max for integration test

    def test_caching_integration(self):
        """Test that caching works across the full pipeline"""
        from src.neoc_assistant.rag_pipeline import rag_pipeline

        with patch.object(
            rag_pipeline.rag_chain, "invoke", return_value="Cached response"
        ):
            # First request
            result1 = rag_pipeline.process_query("test query")
            first_time = result1.get("processing_time", 0)

            # Second identical request (should use cache)
            result2 = rag_pipeline.process_query("test query")
            second_time = result2.get("processing_time", 0)

            # Results should be identical
            assert result1["response"] == result2["response"]

            # Second request should be faster (cached)
            if first_time > 0 and second_time > 0:
                assert second_time <= first_time

    def test_memory_management_integration(self):
        """Test memory management under load"""
        from src.neoc_assistant.rag_pipeline import rag_pipeline

        initial_memory = rag_pipeline.current_memory_usage

        # Simulate multiple conversations
        for i in range(50):
            rag_pipeline._add_to_conversation_memory(
                f"conv_{i % 10}",  # Reuse conversation IDs
                f"Question {i}",
                f"Response {i}" * 50,  # Large responses
            )

        # Memory should be managed
        rag_pipeline._cleanup_memory()
        final_memory = rag_pipeline.current_memory_usage

        # Should not exceed memory limits
        assert final_memory <= rag_pipeline.max_memory_mb * 1024 * 1024

    def test_error_recovery_integration(self):
        """Test system recovers from errors gracefully"""
        from src.neoc_assistant.rag_pipeline import rag_pipeline

        # Test with failing components
        with patch.object(
            rag_pipeline.rag_chain, "invoke", side_effect=Exception("Test error")
        ):
            result = rag_pipeline.process_query("test query")

            assert result["success"] is False
            assert "error" in result
            assert "Error:" in result["response"]

    def test_performance_metrics_integration(self):
        """Test performance metrics are collected"""
        from src.neoc_assistant.llm_service import llm_service
        from src.neoc_assistant.rag_pipeline import rag_pipeline

        # Make some requests
        with patch.object(rag_pipeline.rag_chain, "invoke", return_value="Test"):
            for i in range(5):
                rag_pipeline.process_query(f"Query {i}")

        # Check metrics
        rag_metrics = rag_pipeline.get_performance_metrics()
        llm_metrics = llm_service.get_performance_metrics()

        assert rag_metrics["total_queries"] >= 5
        assert llm_metrics["total_requests"] >= 5
        assert "avg_response_time" in rag_metrics
        assert "cache_hit_rate" in rag_metrics
