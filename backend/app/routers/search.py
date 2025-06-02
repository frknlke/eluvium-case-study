from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from ..services.vectorStore import ChromaVectorStore

router = APIRouter(
    prefix="/api/search",
    tags=["search"]
)

# Initialize the vector store
vector_store = ChromaVectorStore(collection_name="emails")

class SearchQuery(BaseModel):
    """Search query model for semantic search"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 5

class AdvancedSearchQuery(BaseModel):
    """Advanced search query with entity filters and date ranges"""
    query: str = Field(..., description="Semantic search query text")
    entities: Optional[Dict[str, List[str]]] = Field(None, description="Entity filters by type (e.g. {'PERSON': ['John'], 'ORG': ['Acme']})")
    date_from: Optional[datetime] = Field(None, description="Start date for filtering")
    date_to: Optional[datetime] = Field(None, description="End date for filtering")
    limit: int = Field(5, description="Maximum number of results to return")

class SearchResult(BaseModel):
    """Search result model"""
    id: str
    document: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None

@router.post("/semantic", response_model=List[SearchResult])
async def semantic_search(search_query: SearchQuery):
    """
    Search for semantically similar emails based on text query
    
    The search uses vector embeddings to find similar content
    """
    try:
        results = vector_store.search_similar(
            query=search_query.query,
            n_results=search_query.limit,
            filter_criteria=search_query.filters
        )
        
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform semantic search: {str(e)}"
        )

@router.post("/advanced", response_model=List[SearchResult])
async def advanced_search(search_query: AdvancedSearchQuery):
    """
    Advanced search with entity filtering and date ranges
    
    Combines semantic search with structured filters
    """
    try:
        # Build filter criteria based on provided entities and dates
        filter_criteria = {}
        
        # Handle entity filters
        if search_query.entities:
            for entity_type, values in search_query.entities.items():
                if values and len(values) > 0:
                    # For each entity value, create a contains filter
                    for i, value in enumerate(values):
                        # Use a numbered key to avoid overwriting multiple filters of same type
                        filter_criteria[f"{entity_type}_contains_{i}"] = value
        
        # Handle date range filters
        if search_query.date_from:
            filter_criteria["date_gte"] = search_query.date_from.isoformat()
        if search_query.date_to:
            filter_criteria["date_lte"] = search_query.date_to.isoformat()
            
        # Perform search with combined filters
        results = vector_store.search_similar(
            query=search_query.query,
            n_results=search_query.limit,
            filter_criteria=filter_criteria
        )
        
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform advanced search: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_vector_store_stats():
    """Get statistics about the vector store"""
    try:
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vector store stats: {str(e)}"
        )

@router.post("/print-embeddings", response_model=Dict[str, Any])
async def print_embeddings():
    """
    Print all embeddings and their metadata to the backend console
    
    This endpoint is triggered by the "Show Embeddings" button in the dashboard
    """
    try:
        result = vector_store.print_all_embeddings()
        return {
            "success": True,
            "message": f"Printed {result['count']} embeddings to console",
            "count": result["count"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to print embeddings: {str(e)}"
        ) 