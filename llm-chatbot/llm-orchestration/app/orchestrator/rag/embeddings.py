from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingsPipeline:
    """Pipeline for text chunking and embedding."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        try:
            chunks = []
            words = text.split()
            
            # Simple word-based chunking
            for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
                chunk = " ".join(words[i:i + self.chunk_size])
                if chunk:
                    chunks.append(chunk)
            
            logger.info(f"Chunked text into {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk multiple documents."""
        try:
            chunked = []
            
            for doc in documents:
                doc_id = doc.get("id", "")
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                chunks = self.chunk_text(content)
                
                for idx, chunk in enumerate(chunks):
                    chunked.append({
                        "id": f"{doc_id}_chunk_{idx}",
                        "content": chunk,
                        "metadata": {
                            **metadata,
                            "source_id": doc_id,
                            "chunk_index": idx
                        }
                    })
            
            logger.info(f"Chunked {len(documents)} documents into {len(chunked)} chunks")
            return chunked
        
        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            raise
