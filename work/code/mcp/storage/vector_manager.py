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
        if db_path:
            self.db_path = Path(db_path)
        else:
            # This fallback should ideally not be used in the main application flow,
            # as the ProjectManager should always provide an explicit path.
            from . import get_project_root

            project_root = get_project_root()
            self.db_path = project_root / ".srrd" / "data" / "knowledge.db"

        if config_path:
            self.config_path = Path(config_path)
        else:
            base_dir = Path(__file__).resolve().parent.parent
            self.config_path = base_dir / "config" / "vector_collections.yaml"

        self.client = None
        self.collections = {}
        self.embedding_model = None
        self.config = None

    async def initialize(self, enable_embedding_model: bool = False):
        """Initialize vector database and collections"""
        if not CHROMADB_AVAILABLE:
            logger.info(
                "ChromaDB not available. Vector search features will be limited."
            )
            return

        try:
            logger.info("Initializing vector database...")
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(self.db_path))

            if YAML_AVAILABLE and self.config_path.is_file():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning(
                    f"Vector collections config not found at {self.config_path}. Using default."
                )
                self.config = {
                    "vector_collections": {
                        "research_literature": {},
                        "novel_theories": {},
                        "methodologies": {},
                        "interactions": {},
                    }
                }

            logger.info("Setting up collections...")
            collections_config = self.config.get("vector_collections", {})
            for collection_name, collection_config in collections_config.items():
                try:
                    metadata = collection_config.get(
                        "metadata", {"hnsw:space": "cosine"}
                    )
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
            self.client = None
            self.collections = {}
            self.embedding_model = None

    async def add_document(
        self, collection_name: str, document: str, metadata: Dict[str, Any], doc_id: str
    ):
        """Add document to collection with embedding"""
        if not self.client or collection_name not in self.collections:
            logger.warning(
                f"Vector DB not ready or collection '{collection_name}' not found."
            )
            return

        try:
            if self.embedding_model:
                embedding = self.embedding_model.encode([document])[0].tolist()
            else:
                embedding = [
                    float(hash(word) % 1000) / 1000.0 for word in document.split()[:128]
                ]
                embedding.extend([0.0] * (128 - len(embedding)))

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
            return {"documents": [], "metadatas": [], "distances": []}

        if collection not in self.collections:
            logger.warning(
                f"Collection '{collection}' not found. Available collections: {list(self.collections.keys())}"
            )
            return {"documents": [], "metadatas": [], "distances": []}

        try:
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query])[0].tolist()
            else:
                query_embedding = [
                    float(hash(word) % 1000) / 1000.0 for word in query.split()[:128]
                ]
                query_embedding.extend([0.0] * (128 - len(query_embedding)))

            results = self.collections[collection].query(
                query_embeddings=[query_embedding], n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return {"documents": [], "metadatas": [], "distances": []}

    def store_research_content(
        self, content: str, metadata: Dict[str, Any], collection: str = "research_docs"
    ) -> str:
        """Store research content with metadata"""
        if not self.client:
            return "Vector database not available"
        try:
            doc_id = f"doc_{hash(content)}"
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
            cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
            model_cache_path = (
                cache_dir / f"models--sentence-transformers--{model_name}"
            )
            return model_cache_path.exists()
        except Exception:
            return False

    async def enable_embedding_model(self, timeout: float = 30.0) -> bool:
        """Load the embedding model with proper user feedback"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error(
                "sentence-transformers not available. Install with: pip install sentence-transformers"
            )
            return False
        if self.embedding_model is not None:
            return True

        model_name = "all-MiniLM-L6-v2"
        if not self._is_model_cached(model_name):
            logger.info(
                f"Downloading embedding model {model_name} (~90MB)... This may take a moment."
            )

        try:
            loop = asyncio.get_event_loop()
            self.embedding_model = await loop.run_in_executor(
                None, lambda: SentenceTransformer(model_name)
            )
            logger.info("Embedding model loaded successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
            return False

    async def close(self):
        """Close the vector database client"""
        if self.client:
            self.client = None
            self.collections = {}
            self.embedding_model = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize(enable_embedding_model=False)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
