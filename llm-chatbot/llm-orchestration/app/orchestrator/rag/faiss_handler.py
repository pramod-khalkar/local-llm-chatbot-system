from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from pathlib import Path
import logging
import pickle
import os

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS vector database for RAG."""
    
    def __init__(self, index_path: str = "/data/faiss_index", dimension: int = 768):
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension
        self.index = None
        self.metadata = {}
        self.chunks = []
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        index_file = self.index_path / "faiss.index"
        metadata_file = self.index_path / "metadata.pkl"
        chunks_file = self.index_path / "chunks.pkl"
        
        if index_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                with open(chunks_file, 'rb') as f:
                    self.chunks = pickle.load(f)
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"Failed to load index: {str(e)}, creating new")
                self.index = faiss.IndexFlatL2(self.dimension)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info(f"Created new FAISS index with dimension {self.dimension}")
    
    def add_documents(self, embeddings: List[List[float]], chunks: List[str], metadata: List[Dict[str, Any]] = None):
        """Add document chunks with embeddings to index."""
        try:
            if not embeddings:
                logger.warning("No embeddings provided")
                return 0
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings).astype('float32')
            
            # Add to FAISS
            self.index.add(embeddings_array)
            
            # Store metadata
            for i, (chunk, meta) in enumerate(zip(chunks, metadata or [{}] * len(chunks))):
                idx = self.index.ntotal - len(chunks) + i
                self.chunks.append(chunk)
                self.metadata[idx] = meta
            
            # Save index
            self._save_index()
            
            logger.info(f"Added {len(embeddings)} documents to FAISS index")
            return len(embeddings)
        
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search(self, query_embedding: List[float], k: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            if self.index.ntotal == 0:
                logger.warning("Index is empty")
                return []
            
            # Convert to numpy array
            query_array = np.array([query_embedding]).astype('float32')
            logger.info(f"Query embedding shape: {query_array.shape}, dimensions: {query_array.shape[1]}")
            logger.info(f"Index total vectors: {self.index.ntotal}, chunks stored: {len(self.chunks)}")
            
            # Search
            distances, indices = self.index.search(query_array, min(k, self.index.ntotal))
            logger.info(f"Search returned distances: {distances[0]}, indices: {indices[0]}")
            
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0:  # Valid index
                    score = 1 / (1 + dist)  # Convert distance to similarity score
                    logger.info(f"Result idx={idx}, dist={dist}, score={score}, threshold={threshold}")
                    if score >= threshold:
                        results.append({
                            "content": self.chunks[idx] if idx < len(self.chunks) else "",
                            "score": float(score),
                            "metadata": self.metadata.get(idx, {})
                        })
            
            logger.info(f"Search returned {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Error searching index: {str(e)}")
            raise
    
    def _save_index(self):
        """Save index to disk."""
        try:
            self.index_path.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.index_path / "faiss.index"))
            
            with open(self.index_path / "metadata.pkl", 'wb') as f:
                pickle.dump(self.metadata, f)
            
            with open(self.index_path / "chunks.pkl", 'wb') as f:
                pickle.dump(self.chunks, f)
            
            logger.debug("FAISS index saved to disk")
        
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_path": str(self.index_path)
        }
