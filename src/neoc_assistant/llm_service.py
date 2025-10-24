from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import List, Dict, Any, Optional
import logging
import hashlib
import time
from functools import lru_cache
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/llm_service.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class ResponseCache:
    """Thread-safe response cache with TTL"""
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.cache = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]  # Expired
            return None

    def put(self, key: str, value: str) -> None:
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self.cache.keys(),
                               key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            self.cache[key] = (value, time.time())

class LLMService:
    """Optimized LLM service with caching and performance monitoring"""

    def __init__(self, model_name: str = "phi3:latest", cache_size: int = 50):
        self.model_name = model_name
        self.llm = OllamaLLM(
            model=model_name,
            temperature=0.1,  # Lower temperature for more consistent responses
            num_ctx=1024,     # Reduced context window to save memory
            num_thread=1      # Reduced threads to save memory
        )

        # Initialize caches
        self.response_cache = ResponseCache(max_size=cache_size)

        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'total_tokens': 0,
            'avg_response_time': 0.0
        }

        self.setup_chains()
        logger.info(f"LLM Service initialized with model {model_name}")

    def setup_chains(self):
        """Set up LangChain chains for different tasks"""

        # Basic chat chain (simplified for testing)
        self.chat_prompt = PromptTemplate.from_template("""
You are NEOC AI Assistant, a disaster management expert.

Context: {context}

Question: {question}

Please provide a helpful response.
""")

        self.chat_chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | self.chat_prompt
            | self.llm
            | StrOutputParser()
        )

        # RAG chain for retrieval-augmented generation
        self.rag_prompt = PromptTemplate.from_template("""
You are NEOC AI Assistant, a comprehensive disaster management expert with extensive knowledge of all natural hazards, their prediction methodologies, mitigation strategies, and prevention protocols.

Use the following pieces of context to answer the question. If you don't know the answer based on the context, say so clearly and provide general guidance based on your expertise.

Context:
{context}

Question: {question}

Instructions:
1. Answer based on the provided context and your expert knowledge.
2. Be concise, accurate, and professional in your response.
3. If you reference any studies, research, organizations, or specific methodologies in your answer, you MUST include proper citations.
4. All citations must follow IEEE citation style.
5. If any references are used, include a "Bibliography" section at the end of your response with the IEEE-formatted citations.
6. Only include a Bibliography section if references are actually cited in the response.
7. Number the bibliography entries sequentially (e.g., [1], [2], etc.).

Response format:
- Provide your main answer first
- If references are used, add a "Bibliography" section at the end with IEEE citations

Answer:""")

        self.rag_chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | self.rag_prompt
            | self.llm
            | StrOutputParser()
        )

    def generate_response(self, question: str, context: str = "") -> str:
        """Generate response with O(1) caching and performance monitoring"""
        start_time = time.time()
        self.metrics['total_requests'] += 1

        # Input validation
        if not question or not question.strip():
            return "Please provide a valid question."

        # Create cache key
        cache_key = self._generate_cache_key(question, context)

        # Check cache first - O(1)
        cached_response = self.response_cache.get(cache_key)
        if cached_response:
            self.metrics['cache_hits'] += 1
            logger.debug("LLM response cache hit")
            return cached_response

        try:
            # Temporary static response for testing
            response = f"I received your question: '{question}'. This is a test response from NEOC AI Assistant."

            if response:
                response = response.strip()
                # Cache successful responses - O(1)
                self.response_cache.put(cache_key, response)

                # Update metrics
                response_time = time.time() - start_time
                self.metrics['avg_response_time'] = (
                    (self.metrics['avg_response_time'] * (self.metrics['total_requests'] - 1)) +
                    response_time
                ) / self.metrics['total_requests']

                logger.debug(f"LLM response generated in {response_time:.2f}s")
                return response
            else:
                return "I apologize, but I was unable to generate a response."

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"

    def _generate_cache_key(self, question: str, context: str) -> str:
        """Generate cache key - O(1)"""
        combined = f"{question}|{context[:500]}"  # Limit context for key
        return hashlib.md5(combined.encode()).hexdigest()

    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format documents into context string - O(n) time, O(n) space optimization"""
        if not documents:
            return "No relevant context found in the documents."

        # Pre-allocate list for better memory performance
        context_parts = [""] * len(documents)

        # O(n) single pass formatting
        for i, doc in enumerate(documents):
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            source = getattr(doc, 'metadata', {}).get('source', f'Document {i+1}')

            # Limit content length for performance
            if len(content) > 1000:
                content = content[:1000] + "..."

            context_parts[i] = f"Document {i+1} ({source}):\n{content}\n"

        return "".join(context_parts)  # More efficient than join with \n

    def check_ollama_status(self) -> bool:
        """Check if Ollama service is running and model is available - O(1)"""
        try:
            # Quick health check
            test_response = self.llm.invoke("Hi")
            return bool(test_response and test_response.strip())
        except Exception as e:
            logger.error(f"Ollama status check failed: {str(e)}")
            return False

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics - O(1)"""
        cache_hit_rate = (
            self.metrics['cache_hits'] / self.metrics['total_requests']
            if self.metrics['total_requests'] > 0 else 0
        )

        return {
            'total_requests': self.metrics['total_requests'],
            'cache_hit_rate': cache_hit_rate,
            'avg_response_time': self.metrics['avg_response_time'],
            'cache_size': len(self.response_cache.cache),
            'model_name': self.model_name
        }

    def clear_cache(self) -> None:
        """Clear response cache - O(1)"""
        with self.response_cache.lock:
            self.response_cache.cache.clear()
        logger.info("LLM response cache cleared")

# Global instance
llm_service = LLMService()