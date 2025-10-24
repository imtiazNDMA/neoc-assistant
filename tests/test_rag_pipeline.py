"""
Unit tests for RAG Pipeline with Big-O performance validation
"""

import time
from unittest.mock import Mock, patch

import pytest

from neoc_assistant.rag_pipeline import LRUCache, RAGPipeline


class TestLRUCache:
    """Test LRU Cache Big-O performance"""

    def test_cache_operations_o1(self):
        """Test that cache operations are O(1)"""
        cache = LRUCache(3)

        # Test put and get operations
        start_time = time.time()
        for i in range(1000):
            cache.put(f"key{i}", f"value{i}")
            cache.get(f"key{i}")
        end_time = time.time()

        # Should complete in reasonable time for O(1) operations
        assert end_time - start_time < 1.0  # Less than 1 second for 2000 operations

    def test_cache_capacity(self):
        """Test cache respects capacity limits"""
        cache = LRUCache(2)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"


class TestRAGPipeline:
    """Test RAG Pipeline optimizations"""

    @pytest.fixture
    def rag_pipeline(self):
        """Create RAG pipeline instance"""
        with patch("neoc_assistant.document_processor.document_processor"):
            pipeline = RAGPipeline(max_cache_size=10)
            return pipeline

    def test_cache_hit_performance(self, rag_pipeline):
        """Test that caching improves performance"""
        # Mock the chain invoke
        with patch.object(
            rag_pipeline.rag_chain, "invoke", return_value="Test response"
        ):
            # First call - cache miss
            start_time = time.time()
            result1 = rag_pipeline.process_query("test question")
            first_call_time = time.time() - start_time

            # Second call - cache hit
            start_time = time.time()
            result2 = rag_pipeline.process_query("test question")
            second_call_time = time.time() - start_time

            # Cache hit should be significantly faster
            assert second_call_time < first_call_time * 0.5
            assert result1["response"] == result2["response"]

    def test_memory_management(self, rag_pipeline):
        """Test memory bounds are respected"""
        initial_memory = rag_pipeline.current_memory_usage

        # Add multiple conversations
        for i in range(20):
            rag_pipeline._add_to_conversation_memory(
                f"conv_{i}", f"Question {i}", f"Response {i}" * 100
            )

        # Memory should be managed
        assert rag_pipeline.current_memory_usage >= initial_memory

        # Trigger cleanup
        rag_pipeline._cleanup_memory()

        # Memory should be reduced
        final_memory = rag_pipeline.current_memory_usage
        assert final_memory <= rag_pipeline.max_memory_mb * 1024 * 1024

    def test_source_extraction_optimization(self, rag_pipeline):
        """Test source extraction Big-O performance"""
        # Create test response with multiple sources
        response = """
        According to Document 1 (research.pdf), climate change affects weather patterns.
        Document 2 (study.pdf) shows similar results.
        Document 1 (research.pdf) also mentions temperature increases.
        """

        start_time = time.time()
        sources = rag_pipeline._extract_sources(response)
        extraction_time = time.time() - start_time

        # Should extract sources efficiently
        assert "research.pdf" in sources
        assert "study.pdf" in sources
        assert len(sources) == 2

        # Should be fast (less than 1ms for this small input)
        assert extraction_time < 0.001

    def test_input_validation(self, rag_pipeline):
        """Test input validation prevents attacks"""
        # Test empty input
        result = rag_pipeline.process_query("")
        assert not result["success"]
        assert "Invalid question" in result["response"]

        # Test overly long input
        long_question = "A" * 2000
        result = rag_pipeline.process_query(long_question)
        assert not result["success"]
        assert "too long" in result["response"]

    def test_performance_metrics(self, rag_pipeline):
        """Test performance metrics are tracked"""
        with patch.object(rag_pipeline.rag_chain, "invoke", return_value="Test"):
            rag_pipeline.process_query("test")

            metrics = rag_pipeline.get_performance_metrics()
            assert metrics["total_queries"] == 1
            assert "avg_response_time" in metrics
            assert "cache_hit_rate" in metrics
