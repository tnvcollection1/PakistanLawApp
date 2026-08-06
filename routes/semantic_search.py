"""
Semantic Search Module for Pakistan Law App
Uses sentence-transformers for vector embeddings and cosine similarity
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SemanticSearchEngine:
    """Semantic search engine using sentence transformers"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
        self.document_metadata = []
        
    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the search index
        Args:
            documents: List of dicts with 'text' and 'metadata' keys
        """
        self.documents = [doc['text'] for doc in documents]
        self.document_metadata = [doc.get('metadata', {}) for doc in documents]
        
        if self.documents:
            logger.info(f"Encoding {len(self.documents)} documents...")
            self.embeddings = self.model.encode(self.documents, convert_to_numpy=True, show_progress_bar=True)
            logger.info("Document encoding complete")
        else:
            self.embeddings = None
            
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents
        Args:
            query: Search query string
            top_k: Number of results to return
        Returns:
            List of result dicts with score, text, and metadata
        """
        if self.embeddings is None or len(self.documents) == 0:
            return []
            
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                results.append({
                    'score': float(similarities[idx]),
                    'text': self.documents[idx],
                    'metadata': self.document_metadata[idx]
                })
        
        return results
        
    def save_index(self, path: str):
        """Save the index to disk"""
        index_data = {
            'documents': self.documents,
            'metadata': self.document_metadata,
            'embeddings': self.embeddings.tolist() if self.embeddings is not None else None
        }
        
        with open(path, 'w') as f:
            json.dump(index_data, f)
            
    def load_index(self, path: str):
        """Load index from disk"""
        if not os.path.exists(path):
            logger.warning(f"Index file not found: {path}")
            return
            
        with open(path, 'r') as f:
            index_data = json.load(f)
            
        self.documents = index_data['documents']
        self.document_metadata = index_data['metadata']
        
        if index_data['embeddings']:
            self.embeddings = np.array(index_data['embeddings'])
        else:
            self.embeddings = None


class PakistanLawSearch:
    """Specialized search for Pakistani legal content"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.engine = SemanticSearchEngine(model_name)
        self.statutes = {}
        self.cases = {}
        
    def index_statutes(self, statutes_data: List[Dict]):
        """Index statute documents"""
        documents = []
        for statute in statutes_data:
            text = f"{statute.get('title', '')} {statute.get('description', '')} {statute.get('content', '')}"
            documents.append({
                'text': text,
                'metadata': {
                    'type': 'statute',
                    'id': statute.get('id'),
                    'title': statute.get('title'),
                    'category': statute.get('category'),
                    'year': statute.get('year')
                }
            })
            self.statutes[statute.get('id')] = statute
            
        self.engine.add_documents(documents)
        
    def index_cases(self, cases_data: List[Dict]):
        """Index case law documents"""
        documents = []
        for case in cases_data:
            text = f"{case.get('title', '')} {case.get('facts', '')} {case.get('judgment', '')}"
            documents.append({
                'text': text,
                'metadata': {
                    'type': 'case',
                    'id': case.get('id'),
                    'title': case.get('title'),
                    'court': case.get('court'),
                    'year': case.get('year')
                }
            })
            self.cases[case.get('id')] = case
            
        self.engine.add_documents(documents)
        
    def search(self, query: str, filters: Optional[Dict] = None, top_k: int = 10) -> Dict:
        """
        Search across all indexed content
        Args:
            query: Search query
            filters: Optional filters (type, year, category, etc.)
            top_k: Number of results
        Returns:
            Dict with 'statutes' and 'cases' results
        """
        results = self.engine.search(query, top_k * 2)
        
        statutes_results = []
        cases_results = []
        
        for result in results:
            metadata = result['metadata']
            if filters:
                skip = False
                for key, value in filters.items():
                    if key in metadata and metadata[key] != value:
                        skip = True
                        break
                if skip:
                    continue
                    
            if metadata['type'] == 'statute':
                statutes_results.append(result)
            elif metadata['type'] == 'case':
                cases_results.append(result)
                
        return {
            'statutes': statutes_results[:top_k],
            'cases': cases_results[:top_k],
            'total_results': len(statutes_results) + len(cases_results)
        }
        
    def get_document(self, doc_id: str, doc_type: str) -> Optional[Dict]:
        """Get a specific document by ID and type"""
        if doc_type == 'statute':
            return self.statutes.get(doc_id)
        elif doc_type == 'case':
            return self.cases.get(doc_id)
        return None


# Initialize global search instance
_search_instance = None

def get_search_instance() -> PakistanLawSearch:
    """Get or create the global search instance"""
    global _search_instance
    if _search_instance is None:
        _search_instance = PakistanLawSearch()
    return _search_instance

def initialize_search(statutes_data: List[Dict] = None, cases_data: List[Dict] = None):
    """Initialize the search with data"""
    search = get_search_instance()
    
    if statutes_data:
        search.index_statutes(statutes_data)
    if cases_data:
        search.index_cases(cases_data)
        
    logger.info("Search engine initialized")
    
def perform_search(query: str, filters: Optional[Dict] = None, top_k: int = 10) -> Dict:
    """Perform a search query"""
    search = get_search_instance()
    return search.search(query, filters, top_k)
