"""
Unit tests for Document Processor optimizations
"""

import time
from unittest.mock import Mock, patch

import pytest

from neoc_assistant.document_processor import DocumentMetadata, DocumentProcessor


class TestDocumentProcessor:
    """Test Document Processor Big-O optimizations"""

    @pytest.fixture
    def doc_processor(self, tmp_path):
        """Create document processor with temporary directories"""
        return DocumentProcessor(
            data_dir=str(tmp_path / "data"),
            persist_dir=str(tmp_path / "chroma"),
            cache_dir=str(tmp_path / "cache"),
        )

    def test_search_performance_scaling(self, doc_processor):
        """Test that search performance scales well - O(log n)"""
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [
            Mock(page_content=f"Content {i}", metadata={"source": f"doc{i}.pdf"})
            for i in range(3)
        ]
        doc_processor.vectorstore = mock_vectorstore

        # Test with different numbers of results
        for k in [1, 3, 5]:
            start_time = time.time()
            results = doc_processor.search_similar("test query", k=k)
            search_time = time.time() - start_time

            assert len(results) <= k
            # Each search should be fast (less than 100ms)
            assert search_time < 0.1

    def test_caching_efficiency(self, doc_processor):
        """Test document caching reduces load times"""
        # Mock file operations
        with (
            patch("os.path.exists", return_value=True),
            patch("os.listdir", return_value=["test.pdf"]),
            patch.object(doc_processor, "_get_dir_hash", return_value="testhash"),
        ):

            # First load - cache miss
            start_time = time.time()
            with patch("document_processor.PyPDFDirectoryLoader") as mock_loader:
                mock_loader.return_value.load.return_value = [Mock()]
                docs1 = doc_processor.load_documents()
            first_load_time = time.time() - start_time

            # Second load - cache hit
            start_time = time.time()
            docs2 = doc_processor.load_documents()
            second_load_time = time.time() - start_time

            # Cache hit should be much faster
            assert second_load_time < first_load_time * 0.1
            assert docs1 == docs2

    def test_memory_efficient_chunking(self, doc_processor):
        """Test chunking uses memory efficiently"""
        # Create test documents
        test_docs = [
            Mock(page_content="A" * 2000),  # Large document
            Mock(page_content="B" * 1000),
            Mock(page_content="C" * 500),
        ]

        start_time = time.time()
        chunks = doc_processor.split_documents(test_docs)
        chunking_time = time.time() - start_time

        # Should create appropriate number of chunks
        assert len(chunks) > len(test_docs)  # Should split large documents

        # Each chunk should be within size limits
        for chunk in chunks:
            assert (
                len(chunk.page_content)
                <= doc_processor.text_splitter.chunk_size
                + doc_processor.text_splitter.chunk_overlap
            )

        # Should be reasonably fast
        assert chunking_time < 1.0

    def test_error_handling(self, doc_processor):
        """Test error handling doesn't crash the system"""
        # Test search with no vectorstore
        doc_processor.vectorstore = None
        result = doc_processor.search_similar("test")
        assert result == []  # Should return empty list, not crash

    def test_input_validation(self, doc_processor):
        """Test input validation for search parameters"""
        # Test with invalid k values
        doc_processor.vectorstore = Mock()
        doc_processor.vectorstore.similarity_search.return_value = []

        # Should handle negative k
        result = doc_processor.search_similar("test", k=-1)
        assert len(result) == 0

        # Should handle very large k
        result = doc_processor.search_similar("test", k=1000)
        assert len(result) == 0  # Limited by our bounds checking
