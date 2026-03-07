"""
Chroma vector database for semantic memory
"""

import structlog
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from datetime import datetime

logger = structlog.get_logger(__name__)


class VectorStore:
    """Persistent vector store using Chroma"""
    
    def __init__(self, config, embedding_model):
        self.config = config
        self.embedding_model = embedding_model
        
        persist_dir = config.get("memory.vector_db.persist_directory", "./data/vectordb")
        collection_name = config.get("memory.vector_db.collection_name", "jarvis_memory")
        
        logger.info("Initializing vector store", path=persist_dir)
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(
            "✓ Vector store ready",
            collection=collection_name,
            count=self.collection.count()
        )
        
    async def add_memory(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        Add memory node to vector store
        
        Returns: node_id
        """
        from uuid import uuid4
        
        node_id = str(uuid4())
        
        # Generate embedding
        embedding = self.embedding_model.encode_single(text)
        
        # Add metadata
        if metadata is None:
            metadata = {}
            
        metadata["timestamp"] = datetime.now().isoformat()
        
        # Store in Chroma
        self.collection.add(
            ids=[node_id],
            embeddings=[embedding.tolist()],
            documents=[text],
            metadatas=[metadata]
        )
        
        logger.info("Memory added", node_id=node_id, type=metadata.get("type", "unknown"))
        return node_id
        
    async def query(self, query_text: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar memories
        
        Returns: List of matching memory nodes with text and metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode_single(query_text)
        
        # Query Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filter_dict
        )
        
        # Format results
        memories = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                memories.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0.0
                })
                
        logger.info("Memory query", query_len=len(query_text), results=len(memories))
        return memories
        
    async def delete_memory(self, node_id: str):
        """Delete memory node"""
        self.collection.delete(ids=[node_id])
        logger.info("Memory deleted", node_id=node_id)
        
    def count(self) -> int:
        """Get total memory count"""
        return self.collection.count()
        
    async def clear_all(self):
        """Clear all memories (dangerous!)"""
        logger.warning("Clearing all memories")
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
