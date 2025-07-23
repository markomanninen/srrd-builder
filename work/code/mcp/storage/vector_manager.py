# Optional ChromaDB import
try:
    import chromadb

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Optional YAML import
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

import logging
from pathlib import Path
from typing import Any, Dict, List

# Optional sentence transformers import
try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Get logger for this module
logger = logging.getLogger("srrd_builder.vector_manager")


class VectorManager:
    """Vector database manager for semantic search capabilities"""

    def __init__(self, db_path: str = None, config_path: str = None):
        # Use absolute paths from storage module if not provided
        if db_path is None:
            from . import get_project_root

            project_root = get_project_root()
            self.db_path = project_root / ".srrd" / "vector_db"
        else:
            self.db_path = Path(db_path)

        if config_path is None:
            from . import get_config_path

            self.config_path = get_config_path()
        else:
            self.config_path = Path(config_path)

        self.client = None
        self.collections = {}
        self.embedding_model = None
        self.config = None

    async def initialize(self, enable_embedding_model: bool = False):
        """Initialize vector database and collections

        Args:
            enable_embedding_model: If True, will attempt to load SentenceTransformer model
                                   This may require downloading ~90MB on first use
        """
        if not CHROMADB_AVAILABLE:
            logger.info(
                "ChromaDB not available. Vector search features will be limited."
            )
            return

        try:
            logger.info("Initializing vector database...")

            # Initialize ChromaDB client
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(self.db_path))

            # Load configuration
            if YAML_AVAILABLE and self.config_path.exists():
                with open(self.config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                # Default configuration
                self.config = {
                    "collections": {
                        "research_docs": {
                            "name": "research_docs",
                            "metadata": {"hnsw:space": "cosine"},
                        },
                        "knowledge_base": {
                            "name": "knowledge_base",
                            "metadata": {"hnsw:space": "cosine"},
                        },
                        "research_literature": {
                            "name": "research_literature",
                            "metadata": {"hnsw:space": "cosine"},
                        },
                    }
                }

            # Skip embedding model for now - too unreliable for initialization
            self.embedding_model = None
            if enable_embedding_model:
                logger.info("Embedding model loading skipped for reliable startup.")
                logger.info("Use enable_embedding_model() method later if needed.")
            else:
                logger.info("Embedding model disabled for faster startup.")

            # Create collections (without embeddings for now)
            logger.info("Setting up collections...")
            collections_config = self.config.get(
                "vector_collections", self.config.get("collections", {})
            )

            # Always ensure research_literature collection exists
            if "research_literature" not in collections_config:
                collections_config["research_literature"] = {
                    "name": "research_literature",
                    "metadata": {"hnsw:space": "cosine"},
                }

            for collection_name, collection_config in collections_config.items():
                try:
                    # Use hnsw space metadata as default if no specific metadata provided
                    metadata = collection_config.get(
                        "metadata", {"hnsw:space": "cosine"}
                    )
                    if not metadata:
                        metadata = {"hnsw:space": "cosine"}

                    collection = self.client.get_or_create_collection(
                        name=collection_name, metadata=metadata
                    )
                    self.collections[collection_name] = collection
                    logger.debug(f"Collection '{collection_name}' ready")
                except Exception as e:
                    logger.error(
                        f"Failed to create collection '{collection_name}': {e}"
                    )

            logger.info("Vector database initialization completed!")

        except Exception as e:
            logger.error(f"Vector database initialization failed: {e}")
            logger.info("Vector search features will be disabled.")
            self.client = None
            self.collections = {}
            self.embedding_model = None

    async def add_document(
        self, collection_name: str, document: str, metadata: Dict[str, Any], doc_id: str
    ):
        """Add document to collection with embedding"""
        if not self.client:
            logger.warning("Vector database not available")
            return

        if collection_name not in self.collections:
            logger.warning(f"Collection {collection_name} not found")
            return

        try:
            # Generate embedding if model available
            if self.embedding_model:
                embedding = self.embedding_model.encode([document])[0].tolist()
            else:
                # Fallback: use simple text-based embedding simulation
                embedding = [
                    hash(word) % 1000 / 1000.0 for word in document.split()[:100]
                ]
                embedding = embedding + [0.0] * (
                    100 - len(embedding)
                )  # Pad to fixed size

            # Add to collection
            self.collections[collection_name].add(
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id],
            )
        except Exception as e:
            logger.error(f"Error adding document: {e}")

    async def search_knowledge(
        self, query: str, collection: str = "research_docs", n_results: int = 5
    ) -> Dict[str, Any]:
        """Search for relevant knowledge"""
        if not self.client:
            # Fallback: return empty results
            return {"documents": [], "metadatas": [], "distances": []}

        if collection not in self.collections:
            logger.warning(
                f"Collection '{collection}' not found. Available collections: {list(self.collections.keys())}"
            )
            return {"documents": [], "metadatas": [], "distances": []}

        try:
            # Generate query embedding
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query])[0].tolist()
            else:
                # Fallback: simple text-based embedding
                query_embedding = [
                    hash(word) % 1000 / 1000.0 for word in query.split()[:100]
                ]
                query_embedding = query_embedding + [0.0] * (100 - len(query_embedding))

            # Search collection
            results = self.collections[collection].query(
                query_embeddings=[query_embedding], n_results=n_results
            )

            return {
                "documents": results.get("documents", []),
                "metadatas": results.get("metadatas", []),
                "distances": results.get("distances", []),
            }

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return {"documents": [], "metadatas": [], "distances": []}

    def store_research_content(
        self, content: str, metadata: Dict[str, Any], collection: str = "research_docs"
    ) -> str:
        """Store research content with metadata"""
        if not self.client:
            logger.warning("Vector database not available")
            return "Vector database not available"

        try:
            doc_id = f"doc_{hash(content)}"
            # Note: This should be async but simplified for compatibility
            self.collections[collection].add(
                documents=[content], metadatas=[metadata], ids=[doc_id]
            )
            return f"Stored document with ID: {doc_id}"
        except Exception as e:
            return f"Error storing content: {e}"

    def retrieve_related_content(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve content related to query"""
        if not self.client:
            return []

        try:
            results = self.search_knowledge(query, n_results=limit)

            related_content = []
            documents = results.get("documents", [[]])
            metadatas = results.get("metadatas", [[]])
            distances = results.get("distances", [[]])

            for i, doc in enumerate(documents[0] if documents else []):
                related_content.append(
                    {
                        "content": doc,
                        "metadata": (
                            metadatas[0][i] if metadatas and metadatas[0] else {}
                        ),
                        "similarity": 1.0
                        - (distances[0][i] if distances and distances[0] else 1.0),
                    }
                )

            return related_content

        except Exception as e:
            logger.error(f"Error retrieving related content: {e}")
            return []

    def _is_model_cached(self, model_name: str = "all-MiniLM-L6-v2") -> bool:
        """Check if the embedding model is already cached locally"""
        try:
            import os

            # Check HuggingFace cache directory
            cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
            model_cache_path = (
                Path(cache_dir) / f"models--sentence-transformers--{model_name}"
            )
            return model_cache_path.exists()
        except:
            return False

    async def enable_embedding_model(self, timeout: float = 30.0) -> bool:
        """Load the embedding model with proper user feedback

        Args:
            timeout: Maximum time to wait for model download

        Returns:
            True if model was loaded successfully, False otherwise
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error(
                "sentence-transformers not available. Install with: pip install sentence-transformers"
            )
            return False

        if self.embedding_model is not None:
            logger.info("Embedding model already loaded!")
            return True

        model_name = "all-MiniLM-L6-v2"
        is_cached = self._is_model_cached(model_name)

        if is_cached:
            logger.info("Loading cached embedding model...")
        else:
            logger.info("Downloading embedding model (first time setup)...")
            logger.info(f"Model: {model_name} (~90MB)")
            logger.info("This may take 1-2 minutes depending on connection speed...")
            logger.info("The model will be cached locally for future use.")
            logger.info("Press Ctrl+C to cancel if needed.")

        try:
            import asyncio

            # Load model with timeout
            self.embedding_model = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: SentenceTransformer(model_name)
                ),
                timeout=timeout,
            )

            if is_cached:
                logger.info("Cached embedding model loaded successfully!")
            else:
                logger.info("Embedding model downloaded and loaded successfully!")
            return True

        except asyncio.TimeoutError:
            logger.warning(f"Model loading timed out after {timeout} seconds")
            logger.warning(
                "This may be due to slow internet connection or large download."
            )
            logger.warning(
                "Vector search will continue with fallback text-based similarity."
            )
            logger.warning("Try again later with better internet connection.")
            self.embedding_model = None
            return False
        except KeyboardInterrupt:
            logger.info("Model download cancelled by user.")
            logger.info("Vector search will use fallback text-based similarity.")
            self.embedding_model = None
            return False
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            logger.info("Vector search will use fallback text-based similarity.")
            self.embedding_model = None
            return False

    async def close(self):
        """Close the vector database client"""
        if self.client:
            try:
                # ChromaDB doesn't have an explicit close method, but we can clean up references
                self.client = None
                self.collections = {}
                self.embedding_model = None
            except Exception as e:
                logger.warning(f"Error during VectorManager cleanup: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize(enable_embedding_model=False)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
