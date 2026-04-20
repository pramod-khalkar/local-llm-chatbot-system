from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import RagQuery, RagResponse, RagResult
from app.utils.logger import logger
import httpx
from app.config.settings import get_settings

router = APIRouter(prefix="/api/rag", tags=["RAG"])
settings = get_settings()


@router.post("/search", response_model=RagResponse)
async def rag_search(query: RagQuery, db: Session = Depends(get_db)) -> RagResponse:
    """Search documents using RAG (Retrieval Augmented Generation)."""
    try:
        logger.info(f"RAG search query: {query.query}")
        
        # Call orchestration service for RAG
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.orchestration_url}/api/rag/search",
                json=query.dict(),
                timeout=30.0
            )
            if response.status_code != 200:
                raise Exception("Orchestration RAG service error")
            
            rag_results = response.json()
        
        results = [
            RagResult(**result) for result in rag_results.get("results", [])
        ]
        
        return RagResponse(
            results=results,
            query=query.query,
            count=len(results)
        )
    
    except Exception as e:
        logger.error(f"Error in RAG search: {str(e)}")
        raise HTTPException(status_code=500, detail="RAG search failed")


@router.post("/index-documents")
async def index_documents(
    documents: list[dict],
    db: Session = Depends(get_db)
):
    """Index documents for RAG."""
    try:
        logger.info(f"Indexing {len(documents)} documents")
        
        # Call orchestration service to index documents
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.orchestration_url}/api/rag/index",
                json={"documents": documents},
                timeout=60.0
            )
            if response.status_code != 200:
                raise Exception("Orchestration indexing service error")
        
        return {"status": "success", "documents_indexed": len(documents)}
    
    except Exception as e:
        logger.error(f"Error indexing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Document indexing failed")
