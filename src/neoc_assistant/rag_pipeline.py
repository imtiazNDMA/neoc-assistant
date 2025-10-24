import hashlib
import logging
import threading
import time
from collections import OrderedDict
from functools import lru_cache
from typing import Any, Dict, List, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from .document_processor import document_processor
from .llm_service import llm_service

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/rag_pipeline.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


class LRUCache:
    """Thread-safe LRU cache with O(1) operations"""

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.capacity:
                    self.cache.popitem(last=False)  # Remove least recently used
            self.cache[key] = value


class RAGPipeline:
    """Optimized RAG pipeline with O(1) caching and efficient memory management"""

    def __init__(self, max_cache_size: int = 200, max_memory_mb: int = 500):
        # Ensure document processor is initialized
        from .document_processor import document_processor

        if document_processor.vectorstore is None:
            document_processor.create_vectorstore([])

        # Initialize caches for O(1) performance
        self.response_cache = LRUCache(max_cache_size)
        self.context_cache = LRUCache(max_cache_size // 2)

        # Memory-bounded conversation storage
        self.conversation_memory: Dict[str, List[Dict[str, Any]]] = {}
        self.max_memory_mb = max_memory_mb
        self.current_memory_usage = 0

        # Performance metrics
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "avg_response_time": 0.0,
            "total_response_time": 0.0,
        }

        self.setup_rag_chain()
        logger.info("RAG Pipeline initialized with optimized caching")

    def setup_rag_chain(self):
        """Set up the RAG chain using LangChain"""

        # RAG prompt template (simplified for testing)
        self.rag_prompt = PromptTemplate.from_template(
            """
You are NEOC AI Assistant, a disaster management expert.

Context: {context}

Question: {question}

Please provide a helpful response.
"""
        )

        # Create the RAG chain (temporarily simplified for testing)
        self.rag_chain = (
            {
                "context": lambda x: "No context available for testing.",
                "conversation_history": lambda x: "",
                "question": RunnablePassthrough(),
            }
            | self.rag_prompt
            | llm_service.llm
            | StrOutputParser()
        )

    def _get_context(self, inputs: Dict[str, Any]) -> str:
        """Retrieve relevant context with O(1) caching - O(log n) search"""
        question = inputs.get("question", "")
        if not question:
            return "No question provided."

        # Create cache key from question
        cache_key = hashlib.md5(question.encode()).hexdigest()

        # Check cache first - O(1)
        cached_context = self.context_cache.get(cache_key)
        if cached_context:
            logger.debug("Context cache hit")
            return cached_context

        start_time = time.time()
        try:
            # Optimized search with limited results
            docs = document_processor.search_similar(question, k=2)
            context = llm_service.format_context(docs)

            # Cache the result - O(1)
            self.context_cache.put(cache_key, context)

            search_time = time.time() - start_time
            logger.debug(f"Context retrieval took {search_time:.3f}s")
            return context

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return "No context available due to retrieval error."

    def _get_conversation_history(self, inputs: Dict[str, Any]) -> str:
        """Get conversation history with O(1) access to recent items"""
        conversation_id = inputs.get("conversation_id", "default")
        history = self.conversation_memory.get(conversation_id, [])

        if not history:
            return "No previous conversation."

        # Get last 3 exchanges - O(1) slicing
        recent_history = history[-3:] if len(history) >= 3 else history

        # Pre-allocate list for better memory performance
        formatted_history = [""] * (len(recent_history) * 2)
        idx = 0

        # O(k) formatting where k is small constant (3)
        for exchange in recent_history:
            formatted_history[idx] = f"User: {exchange['question']}"
            formatted_history[idx + 1] = f"Assistant: {exchange['response']}"
            idx += 2

        return "\n".join(formatted_history)

    def process_query(
        self, question: str, conversation_id: str = "default", use_crewai: bool = False
    ) -> Dict[str, Any]:
        """Process query with O(1) caching and optimized performance"""
        start_time = time.time()
        self.metrics["total_queries"] += 1

        # Input validation - O(1)
        if not isinstance(question, str) or not question.strip():
            return self._create_error_response(
                "Invalid question provided", conversation_id
            )

        question = question.strip()
        if len(question) > 1000:  # Reasonable limit
            return self._create_error_response("Question too long", conversation_id)

        # Check response cache - O(1)
        cache_key = self._generate_cache_key(question, conversation_id)
        cached_response = self.response_cache.get(cache_key)
        if cached_response:
            self.metrics["cache_hits"] += 1
            logger.info("Response cache hit")
            return cached_response

        try:
            # Process query through optimized RAG chain
            result = self.rag_chain.invoke(
                {"question": question, "conversation_id": conversation_id}
            )
            response = result.strip() if result else "No response generated"

            # Store in conversation memory with memory management
            self._add_to_conversation_memory(conversation_id, question, response)

            # Extract sources efficiently
            sources = self._extract_sources(response)

            # Create response
            response_data = {
                "response": response,
                "conversation_id": conversation_id,
                "sources": sources,
                "success": True,
                "processing_time": time.time() - start_time,
            }

            # Cache successful responses - O(1)
            self.response_cache.put(cache_key, response_data)

            # Update metrics
            self._update_metrics(time.time() - start_time)

            return response_data

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}", exc_info=True)
            return self._create_error_response(str(e), conversation_id)

    def _generate_cache_key(self, question: str, conversation_id: str) -> str:
        """Generate cache key - O(1)"""
        combined = f"{question}:{conversation_id}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _add_to_conversation_memory(
        self, conversation_id: str, question: str, response: str
    ) -> None:
        """Add to conversation memory with memory bounds checking - O(1) amortized"""
        if conversation_id not in self.conversation_memory:
            self.conversation_memory[conversation_id] = []

        # Estimate memory usage (rough approximation)
        memory_estimate = len(question.encode()) + len(response.encode())

        # Add new exchange
        exchange = {
            "question": question,
            "response": response,
            "timestamp": time.time(),
        }

        self.conversation_memory[conversation_id].append(exchange)
        self.current_memory_usage += memory_estimate

        # Memory management - keep only recent conversations
        if self.current_memory_usage > self.max_memory_mb * 1024 * 1024:
            self._cleanup_memory()

    def _cleanup_memory(self) -> None:
        """Clean up memory by removing old conversations - O(n) but infrequent"""
        # Remove conversations older than 1 hour
        cutoff_time = time.time() - 3600
        conversations_to_remove = []

        for conv_id, history in self.conversation_memory.items():
            # Keep only recent exchanges
            recent_history = [
                exchange
                for exchange in history
                if exchange.get("timestamp", 0) > cutoff_time
            ][
                :10
            ]  # Max 10 exchanges per conversation

            if recent_history:
                self.conversation_memory[conv_id] = recent_history
            else:
                conversations_to_remove.append(conv_id)

        # Remove empty conversations
        for conv_id in conversations_to_remove:
            del self.conversation_memory[conv_id]

        # Recalculate memory usage
        self.current_memory_usage = sum(
            len(str(conv).encode()) for conv in self.conversation_memory.values()
        )

    def _create_error_response(
        self, error_msg: str, conversation_id: str
    ) -> Dict[str, Any]:
        """Create standardized error response - O(1)"""
        return {
            "response": f"An error occurred: {error_msg}",
            "conversation_id": conversation_id,
            "sources": [],
            "success": False,
            "error": error_msg,
        }

    def _update_metrics(self, response_time: float) -> None:
        """Update performance metrics - O(1)"""
        self.metrics["total_response_time"] += response_time
        self.metrics["avg_response_time"] = (
            self.metrics["total_response_time"] / self.metrics["total_queries"]
        )

    def _extract_sources(self, response: str) -> List[str]:
        """Extract source references with O(n) time complexity optimization"""
        if not response:
            return []

        sources = set()  # Use set for O(1) lookups
        response_lower = response.lower()  # Case-insensitive search

        # O(n) single pass through response
        words = response_lower.split()
        i = 0
        while i < len(words):
            if words[i] == "document" and i + 1 < len(words):
                # Look for patterns like "Document 1", "Document (source)", etc.
                next_word = words[i + 1]

                # Check for numbered documents
                if next_word.isdigit():
                    sources.add(f"Document {next_word}")
                    i += 2
                    continue

                # Check for parenthetical sources
                remaining = " ".join(words[i:])
                paren_start = remaining.find("(")
                if paren_start != -1:
                    paren_end = remaining.find(")", paren_start)
                    if paren_end != -1:
                        source = remaining[paren_start + 1 : paren_end].strip()
                        if source:
                            sources.add(source)

            i += 1

        return list(sources)  # Convert back to list for API compatibility

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history - O(1) access"""
        return self.conversation_memory.get(conversation_id, []).copy()

    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history - O(1)"""
        if conversation_id in self.conversation_memory:
            del self.conversation_memory[conversation_id]
            return True
        return False

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics - O(1)"""
        cache_hit_rate = (
            self.metrics["cache_hits"] / self.metrics["total_queries"]
            if self.metrics["total_queries"] > 0
            else 0
        )

        return {
            "total_queries": self.metrics["total_queries"],
            "cache_hit_rate": cache_hit_rate,
            "avg_response_time": self.metrics["avg_response_time"],
            "memory_usage_mb": self.current_memory_usage / (1024 * 1024),
            "active_conversations": len(self.conversation_memory),
            "cache_sizes": {
                "response_cache": len(self.response_cache.cache),
                "context_cache": len(self.context_cache.cache),
            },
        }

    def clear_all_caches(self) -> None:
        """Clear all caches - O(1)"""
        self.response_cache.cache.clear()
        self.context_cache.cache.clear()
        logger.info("All caches cleared")


# Global instance
rag_pipeline = RAGPipeline()
