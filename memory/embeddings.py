"""
Embedding model for semantic search
"""

import structlog
from sentence_transformers import SentenceTransformer
import torch

logger = structlog.get_logger(__name__)


class EmbeddingModel:
    """Generates embeddings for text using sentence-transformers"""
    
    def __init__(self, config):
        self.config = config
        
        model_name = config.get("memory.embeddings.model", "sentence-transformers/all-MiniLM-L6-v2")
        device = config.get("memory.embeddings.device", "cpu")
        
        logger.info("Loading embedding model", model=model_name, device=device)
        
        try:
            self.model = SentenceTransformer(model_name, device=device)
            logger.info("✓ Embedding model loaded")
        except Exception as e:
            logger.error("Failed to load embedding model", error=str(e))
            raise
            
    def encode(self, texts: list[str]) -> list:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors (as numpy arrays)
        """
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings
        
    def encode_single(self, text: str):
        """Generate embedding for single text"""
        return self.encode([text])[0]
