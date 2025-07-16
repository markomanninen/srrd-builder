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
import json

# Optional sentence transformers import
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class VectorManager:
    """Vector database manager for semantic search capabilities"""
    
    def __init__(self, db_path: str = "data/vector_db", config_path: str = "config/vector_collections.yaml"):
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
                
        except Exception as e:
            print(f"Warning: Vector database initialization failed: {e}")
            self.client = None
    
    async def add_document(self, collection_name: str, document: str, 
                          metadata: Dict[str, Any], doc_id: str):
        """Add document to collection with embedding"""
        if not self.client:
            print("Vector database not available")
            return
            
        if collection_name not in self.collections:
            print(f"Collection {collection_name} not found")
            return
        
        try:
            # Generate embedding if model available
            if self.embedding_model:
                embedding = self.embedding_model.encode([document])[0].tolist()
            else:
                # Fallback: use simple text-based embedding simulation
                embedding = [hash(word) % 1000 / 1000.0 for word in document.split()[:100]]
                embedding = embedding + [0.0] * (100 - len(embedding))  # Pad to fixed size
            
            # Add to collection
            self.collections[collection_name].add(
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
        except Exception as e:
            print(f"Error adding document: {e}")
    
    async def search_knowledge(self, query: str, collection: str = "research_docs", 
                             n_results: int = 5) -> Dict[str, Any]:
        """Search for relevant knowledge"""
        if not self.client or collection not in self.collections:
            # Fallback: return empty results
            return {
                "documents": [],
                "metadatas": [],
                "distances": []
            }
        
        try:
            # Generate query embedding
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query])[0].tolist()
            else:
                # Fallback: simple text-based embedding
                query_embedding = [hash(word) % 1000 / 1000.0 for word in query.split()[:100]]
                query_embedding = query_embedding + [0.0] * (100 - len(query_embedding))
            
            # Search collection
            results = self.collections[collection].query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return {
                "documents": results.get("documents", []),
                "metadatas": results.get("metadatas", []),
                "distances": results.get("distances", [])
            }
            
        except Exception as e:
            print(f"Error searching: {e}")
            return {
                "documents": [],
                "metadatas": [],
                "distances": []
            }
    
    def store_research_content(self, content: str, metadata: Dict[str, Any], 
                             collection: str = "research_docs") -> str:
        """Store research content with metadata"""
        if not self.client:
            print("Vector database not available")
            return "Vector database not available"
        
        try:
            doc_id = f"doc_{hash(content)}"
            # Note: This should be async but simplified for compatibility
            self.collections[collection].add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return f"Stored document with ID: {doc_id}"
        except Exception as e:
            return f"Error storing content: {e}"
    
    def retrieve_related_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
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
                related_content.append({
                    "content": doc,
                    "metadata": metadatas[0][i] if metadatas and metadatas[0] else {},
                    "similarity": 1.0 - (distances[0][i] if distances and distances[0] else 1.0)
                })
            
            return related_content
            
        except Exception as e:
            print(f"Error retrieving related content: {e}")
            return []
