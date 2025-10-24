# System Components

Detailed documentation of NEOC AI Assistant's core components and their interactions.

## Core Services

### LLM Service

The LLM Service handles all interactions with large language models, providing chat responses and RAG-enhanced answers.

#### Architecture

```python
class LLMService:
    """Optimized LLM service with caching and monitoring"""

    def __init__(self):
        self.llm = Ollama(model=config.llm.model_name)
        self.cache = ResponseCache(max_size=config.llm.cache_size)
        self.chat_prompt = PromptTemplate.from_template(CHAT_TEMPLATE)
        self.rag_prompt = PromptTemplate.from_template(RAG_TEMPLATE)

        # Build chains
        self.chat_chain = self._build_chat_chain()
        self.rag_chain = self._build_rag_chain()
```

#### Key Features

**Response Caching:**
- LRU cache with TTL-based expiration
- Thread-safe operations
- Memory-efficient storage
- Cache hit ratio monitoring

**Prompt Engineering:**
- Disaster management expertise prompts
- IEEE citation requirements
- Context-aware responses
- Error handling instructions

**Performance Monitoring:**
- Response time tracking
- Token usage monitoring
- Error rate calculation
- Model health checks

#### Methods

```python
def generate_response(self, message: str) -> str:
    """Generate chat response with caching"""
    cache_key = self._generate_cache_key(message)

    # Check cache first
    cached = self.cache.get(cache_key)
    if cached:
        return cached

    # Generate new response
    response = self.chat_chain.invoke({"question": message})

    # Cache response
    self.cache.put(cache_key, response)

    return response

def generate_rag_response(self, message: str, context: str) -> str:
    """Generate RAG-enhanced response"""
    return self.rag_chain.invoke({
        "context": context,
        "question": message
    })
```

### RAG Pipeline

Retrieval-Augmented Generation pipeline that enhances responses with relevant document context.

#### Architecture

```python
class RAGPipeline:
    """RAG pipeline with optimized retrieval and generation"""

    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.vectorstore = Chroma(
            persist_directory=config.database.persist_dir,
            embedding_function=self.document_processor.embeddings
        )
        self.llm_service = LLMService()
        self.cache = RAGCache(max_size=config.rag.max_cache_size)
```

#### Components

**Document Processor:**
- Text extraction from various formats
- Semantic chunking
- Embedding generation
- Metadata extraction

**Vector Store:**
- ChromaDB for efficient similarity search
- Persistent storage
- Index optimization
- Batch operations

**Retrieval Strategy:**
- Hybrid search (semantic + keyword)
- Relevance filtering
- Diversity ranking
- Context window management

#### Optimization Features

**Caching:**
- Query-result caching
- Embedding caching
- Context caching
- TTL-based expiration

**Performance:**
- Async document processing
- Batch embedding generation
- Parallel retrieval
- Memory pooling

### Document Processor

Handles document ingestion, processing, and indexing for the RAG system.

#### Supported Formats

- **PDF**: PyPDF2 for text extraction
- **Text**: Direct processing
- **Markdown**: Structure preservation
- **HTML**: BeautifulSoup parsing
- **CSV/JSON**: Structured data handling

#### Processing Pipeline

```python
def process_document(self, file_path: str) -> List[Document]:
    """Process document into chunks"""
    # 1. Extract text
    text = self._extract_text(file_path)

    # 2. Extract metadata
    metadata = self._extract_metadata(file_path)

    # 3. Split into chunks
    chunks = self._split_text(text, metadata)

    # 4. Generate embeddings
    embeddings = self._generate_embeddings(chunks)

    return chunks
```

#### Chunking Strategies

**Semantic Chunking:**
- Sentence-aware splitting
- Context preservation
- Overlap management
- Size optimization

**Metadata Enrichment:**
- Document source
- Creation date
- Author information
- Content type
- Relevance scores

### Security Manager

Comprehensive security layer protecting the application from various threats.

#### Components

**Rate Limiting:**
```python
class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_minute / 60.0
        self.buckets: Dict[str, Dict[str, float]] = defaultdict(dict)
```

**Input Validation:**
- XSS prevention
- SQL injection protection
- Content length limits
- File type validation

**Authentication:**
- API key validation
- JWT token handling
- Session management
- Secure storage

#### Security Features

**Request Filtering:**
- IP-based blocking
- User agent validation
- Request size limits
- Content type checking

**Audit Logging:**
- Security events
- Access attempts
- Error conditions
- Performance metrics

### Monitoring System

Comprehensive observability and performance monitoring.

#### Metrics Collection

```python
class MonitoringSystem:
    """System monitoring and metrics"""

    def __init__(self):
        self.metrics = {
            'requests_total': Counter('requests_total', 'Total requests'),
            'response_time': Histogram('response_time', 'Response time'),
            'errors_total': Counter('errors_total', 'Total errors'),
            'memory_usage': Gauge('memory_usage', 'Memory usage')
        }
```

#### Health Checks

**System Health:**
- CPU usage
- Memory usage
- Disk space
- Network connectivity

**Service Health:**
- Database connectivity
- LLM service availability
- Vector store status
- External service health

#### Alerting

**Threshold-based Alerts:**
- High memory usage
- Slow response times
- Error rate spikes
- Service unavailability

**Automated Responses:**
- Service restart
- Load shedding
- Traffic throttling
- Notification dispatch

## Data Layer

### Vector Store

ChromaDB-based vector storage for document embeddings and similarity search.

#### Configuration

```python
vectorstore = Chroma(
    persist_directory=config.database.persist_dir,
    embedding_function=embeddings,
    collection_name="neoc_documents"
)
```

#### Operations

**Document Storage:**
- Batch insertion
- Metadata storage
- Index updates
- Duplicate handling

**Similarity Search:**
- Cosine similarity
- Euclidean distance
- Query expansion
- Result filtering

### Cache Layer

Multi-level caching system for performance optimization.

#### Cache Types

**Memory Cache:**
- Fast access
- Limited size
- Process-local
- LRU eviction

**Redis Cache:**
- Distributed
- Persistent
- High availability
- Cluster support

**File Cache:**
- Large objects
- Persistent storage
- Compression
- Integrity checks

#### Cache Strategy

```python
class MultiLevelCache:
    """Multi-level caching with fallback"""

    def get(self, key: str):
        # Try memory first
        value = self.memory_cache.get(key)
        if value:
            return value

        # Try Redis
        value = self.redis_cache.get(key)
        if value:
            self.memory_cache.put(key, value)
            return value

        # Try file cache
        value = self.file_cache.get(key)
        if value:
            self.memory_cache.put(key, value)
            self.redis_cache.put(key, value)
            return value

        return None
```

## External Interfaces

### Ollama Integration

Local LLM inference using Ollama.

#### Model Management

```python
class OllamaManager:
    """Ollama model management"""

    def __init__(self, model_name: str = "phi3:latest"):
        self.model_name = model_name
        self.client = ollama.Client()

    def generate(self, prompt: str) -> str:
        """Generate response from Ollama"""
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            options={
                "temperature": config.llm.temperature,
                "num_ctx": config.llm.context_window
            }
        )
        return response['response']
```

#### Model Features

- Local inference
- Multiple model support
- GPU acceleration
- Custom model loading

### API Clients

HTTP clients for external service communication.

#### Configuration

```python
class APIClient:
    """Robust API client with retry logic"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = timeout

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
```

#### Features

- Automatic retries
- Connection pooling
- Timeout handling
- Error recovery

## Configuration Management

### Configuration Structure

```python
@dataclass
class AppConfig:
    """Application configuration"""

    # Database settings
    database: DatabaseConfig

    # LLM settings
    llm: LLMConfig

    # RAG settings
    rag: RAGConfig

    # API settings
    api: APIConfig

    # Security settings
    security: SecurityConfig

    # Logging settings
    logging: LoggingConfig
```

### Environment-based Configuration

```python
def load_config() -> AppConfig:
    """Load configuration from environment"""
    return AppConfig(
        database=DatabaseConfig(
            persist_dir=os.getenv("DB_PERSIST_DIR", "chroma_db")
        ),
        llm=LLMConfig(
            model_name=os.getenv("LLM_MODEL", "phi3:latest"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1"))
        ),
        # ... other configs
    )
```

### Validation

```python
def validate_config(config: AppConfig) -> bool:
    """Validate configuration"""
    checks = [
        config.llm.temperature >= 0 and config.llm.temperature <= 1,
        config.api.port > 0 and config.api.port < 65536,
        Path(config.database.persist_dir).exists() or True,  # Allow creation
    ]

    return all(checks)
```

## Error Handling

### Exception Hierarchy

```python
class NEOCException(Exception):
    """Base exception for NEOC"""
    pass

class LLMError(NEOCException):
    """LLM service errors"""
    pass

class DocumentError(NEOCException):
    """Document processing errors"""
    pass

class SecurityError(NEOCException):
    """Security-related errors"""
    pass
```

### Error Recovery

```python
def with_error_recovery(func):
    """Decorator for error recovery"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except LLMError as e:
            logger.error(f"LLM error: {e}")
            return fallback_response()
        except DocumentError as e:
            logger.error(f"Document error: {e}")
            return error_response("Document processing failed")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return error_response("Internal server error")
    return wrapper
```

## Performance Optimizations

### Memory Management

```python
class MemoryPool:
    """Memory pool for expensive objects"""

    def __init__(self, max_size: int = 10):
        self.pool = Queue(maxsize=max_size)
        self.lock = Lock()

    def get(self):
        """Get object from pool"""
        with self.lock:
            if not self.pool.empty():
                return self.pool.get()
            return self._create_object()

    def put(self, obj):
        """Return object to pool"""
        with self.lock:
            if self.pool.full():
                return  # Discard if full
            self.pool.put(obj)
```

### Async Processing

```python
async def process_batch(self, items: List[dict]) -> List[dict]:
    """Process items asynchronously"""
    tasks = []
    semaphore = asyncio.Semaphore(10)  # Limit concurrency

    async def process_item(item):
        async with semaphore:
            return await self._process_single_item(item)

    for item in items:
        task = asyncio.create_task(process_item(item))
        tasks.append(task)

    return await asyncio.gather(*tasks)
```

This detailed component documentation provides a comprehensive understanding of NEOC AI Assistant's architecture and implementation details.