import chromadb
import os
import hashlib
from typing import Dict, List, Any, Optional, Union
import json
from chromadb.errors import NotFoundError
import re

class ChromaVectorStore:
    """
    A class to handle document storage in Chroma DB
    """
    def __init__(self, collection_name: str = "emails"):
        """
        Initialize the Chroma client and collection
        
        Args:
            collection_name: Name of the collection to store documents
        """
        # Initialize Chroma client - use persistent storage
        persist_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Using existing collection: {collection_name}")
        except NotFoundError:
            # Create collection without embeddings (metadata only)
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"} # Default similarity metric
            )
            print(f"Created new collection: {collection_name}")

    def _generate_simple_embedding(self, text: str) -> List[float]:
        """
        Generate a very simple embedding based on hash of text
        This is not a real embedding, just a placeholder for demonstration
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of embedding values
        """
        # Create a hash of the text
        hash_object = hashlib.md5(text.encode())
        hash_hex = hash_object.hexdigest()
        
        # Convert hash to a list of 10 float values between -1 and 1
        embedding = []
        for i in range(0, len(hash_hex), 3):
            if i+3 <= len(hash_hex):
                # Convert 3 hex chars to an integer, then scale to [-1, 1]
                value = int(hash_hex[i:i+3], 16) / 4095 * 2 - 1
                embedding.append(value)
                if len(embedding) >= 10:  # Limit to 10 dimensions
                    break
        
        return embedding

    def add_email_embedding(self, 
                           email_id: str, 
                           email_content: str, 
                           ner_result: Dict[str, Any]) -> None:
        """
        Add email content to Chroma with NER results as metadata
        
        Args:
            email_id: UUID of the email (from PostgreSQL)
            email_content: Text content of the email
            ner_result: Named entity recognition results for metadata
        """
        # Generate a simple placeholder embedding
        embedding = self._generate_simple_embedding(email_content)
        
        # Prepare metadata (convert complex types to strings for Chroma)
        metadata = {}
        for key, value in ner_result.items():
            if isinstance(value, (list, dict)):
                metadata[key] = json.dumps(value)
            else:
                metadata[key] = str(value) if value is not None else ""
        
        # Add to collection
        self.collection.add(
            ids=[email_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[email_content]
        )
        print(f"Added document for email ID {email_id} to Chroma")
    
    def _process_filter_criteria(self, filter_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process filter criteria to handle special cases like contains, date ranges, etc.
        
        Args:
            filter_criteria: Original filter criteria
            
        Returns:
            Processed filter criteria for Chroma
        """
        if not filter_criteria:
            return {}
            
        chroma_filters = {}
        
        # Process each filter
        for key, value in filter_criteria.items():
            # Handle special suffix operators
            if key.endswith("_contains"):
                base_key = key.replace("_contains", "")
                # For contains, we use Chroma's $contains operator
                chroma_filters[f"$contains:{base_key}"] = value
            elif key.endswith("_gte"):
                base_key = key.replace("_gte", "")
                chroma_filters[f"${base_key}"] = {"$gte": value}
            elif key.endswith("_lte"):
                base_key = key.replace("_lte", "")
                chroma_filters[f"${base_key}"] = {"$lte": value}
            else:
                # Default exact match
                chroma_filters[key] = value
                
        return chroma_filters
    
    def search_similar(self, 
                      query: str, 
                      n_results: int = 5, 
                      filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar emails based on text query
        
        Args:
            query: Text to search for
            n_results: Number of results to return
            filter_criteria: Optional metadata filters
            
        Returns:
            List of matching documents with their IDs and metadata
        """
        # Generate a simple placeholder embedding for the query
        query_embedding = self._generate_simple_embedding(query)
        
        # Process filter criteria if provided
        processed_filters = self._process_filter_criteria(filter_criteria) if filter_criteria else None
        
        # Execute search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=processed_filters
        )
        
        # Format results
        formatted_results = []
        if results and 'ids' in results and results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results.get('distances', [[]])[0][i] if results.get('distances') else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def delete_email(self, email_id: str) -> None:
        """
        Delete an email document from Chroma
        
        Args:
            email_id: UUID of the email to delete
        """
        self.collection.delete(ids=[email_id])
        print(f"Deleted document for email ID {email_id} from Chroma")
    
    def print_all_embeddings(self) -> Dict[str, Any]:
        """
        Get all documents with their metadata and print to console
        
        Returns:
            Dictionary with summary of documents
        """
        # Get all items in the collection
        if self.collection.count() == 0:
            print("No documents found in the collection")
            return {"count": 0, "ids": []}
            
        results = self.collection.get()
        
        print("\n==== CHROMA DATABASE CONTENTS ====")
        print(f"Total documents: {len(results['ids'])}")
        print("================================")
        
        # Print each item with its metadata
        for i, email_id in enumerate(results['ids']):
            print(f"\nEMAIL ID: {email_id}")
            print(f"METADATA: {json.dumps(results['metadatas'][i], indent=2)}")
            
            # Print a snippet of the document text (first 100 chars)
            doc_text = results['documents'][i]
            snippet = doc_text[:100] + "..." if len(doc_text) > 100 else doc_text
            print(f"DOCUMENT SNIPPET: {snippet}")
            print("--------------------------------")
        
        return {
            "count": len(results['ids']),
            "ids": results['ids']
        }
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics
        
        Returns:
            Dictionary with collection statistics
        """
        return {
            "count": self.collection.count(),
            "name": self.collection.name
        } 