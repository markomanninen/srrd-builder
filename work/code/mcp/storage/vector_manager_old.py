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

from pathlib import Path
from typing import List, Dict, Any, Optional

# Optional numpy import
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Optional sentence transformers import
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class VectorManager:
    """Vector database manager for semantic search capabilities"""
    
    def __init__(self, db_path: str, config_path: str = "config/vector_collections.yaml"):
        self.db_path = Path(db_path)
        self.config_path = Path(config_path)
        self.client = None
        self.collections = {}
        self.embedding_model = None
        self.config = None
        
    async def initialize(self):
        """Initialize vector database and collections"""
        if not CHROMADB_AVAILABLE:
            print("Warning: ChromaDB not available. Vector operations will be limited.")
            return
        
        try:
            # Load configuration
            if YAML_AVAILABLE and self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
            else:
                # Default configuration
                self.config = {
                    "vector_collections": {
                        "research_docs": {
                            "name": "research_documents",
                            "description": "Research documents and papers"
                        }
                    }
                }
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=str(self.db_path))
            
            # Initialize embedding model if available
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create collections
            for collection_name, collection_config in self.config['vector_collections'].items():
                try:
                    collection = self.client.get_collection(collection_name)
                except:
                    collection = self.client.create_collection(
                    name=collection_name,
                    metadata=collection_config
                )
            self.collections[collection_name] = collection
    
    async def add_document(self, collection_name: str, document: str, 
                          metadata: Dict[str, Any], doc_id: str):
        """Add document to collection with embedding"""
        if collection_name not in self.collections:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Generate embedding
        embedding = self.embedding_model.encode([document])[0].tolist()
        
        # Add to collection
        self.collections[collection_name].add(
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata],
            ids=[doc_id]
        )
    
    async def search(self, collection_name: str, query: str, 
                    filters: Optional[Dict[str, Any]] = None, 
                    limit: int = 10, novel_theory_boost: bool = False) -> List[Dict[str, Any]]:
        """Perform semantic search in collection"""
        if collection_name not in self.collections:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Prepare search parameters
        search_limit = limit
        if novel_theory_boost:
            search_limit = int(limit * self.config['search_settings']['novel_theory_boost'])
        
        # Perform search
        results = self.collections[collection_name].query(
            query_embeddings=[query_embedding],
            n_results=search_limit,
            where=filters
        )
        
        # Format results
        formatted_results = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            formatted_results.append({
                'document': doc,
                'metadata': metadata,
                'similarity': 1 - distance,  # Convert distance to similarity
                'rank': i + 1
            })
        
        return formatted_results[:limit]
    
    async def search_novel_theories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Specialized search for novel theory development"""
        return await self.search(
            collection_name="novel_theories",
            query=query,
            limit=limit,
            novel_theory_boost=True
        )
    
    async def search_methodologies(self, domain: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for research methodologies in specific domain"""
        filters = {"domain": domain} if domain else None
        return await self.search(
            collection_name="methodologies",
            query=query,
            filters=filters,
            limit=limit
        )
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        if collection_name not in self.collections:
            raise ValueError(f"Collection {collection_name} not found")
        
        collection = self.collections[collection_name]
        count = collection.count()
        
        return {
            "name": collection_name,
            "document_count": count,
            "metadata": collection.metadata
        }
