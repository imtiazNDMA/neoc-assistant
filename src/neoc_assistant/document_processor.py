try:
    from langchain_community.document_loaders import PyPDFDirectoryLoader
except ImportError:
    from langchain.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
from typing import List, Optional, Dict, Any
import logging
import hashlib
import pickle
from functools import lru_cache
import time
from dataclasses import dataclass

# Configure logging with proper levels
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DocumentMetadata:
    """Metadata for document chunks with O(1) access"""
    doc_id: str
    chunk_id: int
    source: str
    page: Optional[int] = None
    total_chunks: int = 0

class DocumentProcessor:
    """Optimized document processor with O(log n) search and caching"""

    def __init__(self, data_dir: str = "data", persist_dir: str = "chroma_db",
                 cache_dir: str = ".cache"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self.cache_dir = cache_dir
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            cache_folder=os.path.join(cache_dir, "embeddings")
        )
        # Optimized chunking for better retrieval
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,  # Power of 2 for better memory alignment
            chunk_overlap=64,  # Reduced overlap for efficiency
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]  # Hierarchical splitting
        )
        self.vectorstore: Optional[Chroma] = None
        self.document_cache: Dict[str, List[Document]] = {}
        self.embedding_cache: Dict[str, List[float]] = {}

        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "embeddings"), exist_ok=True)

        # Initialize vectorstore lazily
        self._init_vectorstore()

    def _init_vectorstore(self) -> None:
        """Lazy initialization of vectorstore with error handling"""
        try:
            if os.path.exists(self.persist_dir):
                logger.info(f"Loading existing vectorstore from {self.persist_dir}")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings
                )
            else:
                logger.info("Vectorstore will be created when documents are ingested")
        except Exception as e:
            logger.error(f"Failed to initialize vectorstore: {e}")
            self.vectorstore = None

    @lru_cache(maxsize=32)  # O(1) cache for repeated loads
    def load_documents(self) -> List[Document]:
        """Load all PDF documents from the data directory - O(n) time, O(n) space"""
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Data directory {self.data_dir} not found")

        cache_key = self._get_dir_hash()
        if cache_key in self.document_cache:
            logger.info("Loading documents from cache")
            return self.document_cache[cache_key]

        start_time = time.time()
        loader = PyPDFDirectoryLoader(self.data_dir)
        documents = loader.load()

        load_time = time.time() - start_time
        logger.info(f"Loaded {len(documents)} documents in {load_time:.2f}s")

        # Cache the loaded documents
        self.document_cache[cache_key] = documents
        return documents

    def _get_dir_hash(self) -> str:
        """Generate hash of directory contents for caching - O(m) where m is file count"""
        file_paths = []
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith('.pdf'):
                    file_paths.append(os.path.join(root, file))

        # Sort for consistent hashing
        file_paths.sort()
        combined = ''.join(file_paths)
        return hashlib.md5(combined.encode()).hexdigest()

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks"""
        splits = self.text_splitter.split_documents(documents)
        logger.info(f"Split into {len(splits)} chunks")
        return splits

    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """Create and persist Chroma vectorstore"""
        if os.path.exists(self.persist_dir):
            logger.info(f"Loading existing vectorstore from {self.persist_dir}")
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        else:
            logger.info("Creating new vectorstore")
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_dir
            )
            self.vectorstore.persist()

        return self.vectorstore

    def add_documents(self, documents: List[Document]):
        """Add new documents to existing vectorstore"""
        if self.vectorstore is None:
            self.create_vectorstore([])

        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
        logger.info(f"Added {len(documents)} documents to vectorstore")

    def search_similar(self, query: str, k: int = 3) -> List[Document]:
        """Search for similar documents - O(log n) with optimized parameters"""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Call create_vectorstore() first.")

        # Limit k to reasonable bounds for performance
        k = min(max(k, 1), 10)  # O(1) bounds checking

        start_time = time.time()
        try:
            # Use optimized search parameters
            docs = self.vectorstore.similarity_search(
                query=query,
                k=k
            )
            search_time = time.time() - start_time
            logger.debug(f"Vector search completed in {search_time:.3f}s for query: {query[:50]}...")
            return docs
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []

    def ingest_all_documents(self):
        """Complete pipeline: load, split, and store all documents"""
        try:
            documents = self.load_documents()
            if not documents:
                logger.warning("No documents found to ingest")
                return

            splits = self.split_documents(documents)
            self.create_vectorstore(splits)
            logger.info("Document ingestion completed successfully")
        except Exception as e:
            logger.error(f"Error during document ingestion: {str(e)}")
            raise

# Global instance for use across the application
document_processor = DocumentProcessor()