import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

class VectorSearch:
    def __init__(self, documents=None):
        self.documents = documents or []
        self.vectorizer = TfidfVectorizer()
        self.vectors = None
        if self.documents:
            self._fit()

    def _fit(self):
        texts = [doc.get('text', '') for doc in self.documents]
        self.vectors = self.vectorizer.fit_transform(texts)

    def add_documents(self, new_documents):
        self.documents.extend(new_documents)
        self._fit()

    def search(self, query, top_k=10):
        if self.vectors is None or len(self.documents) == 0:
            return []
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.vectors).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                results.append({
                    "document": self.documents[idx],
                    "score": float(similarities[idx])
                })
        return results

def vector_search(query, documents, top_k=10):
    vs = VectorSearch(documents)
    return vs.search(query, top_k)

if __name__ == '__main__':
    docs = [
        {"id": 1, "text": "The Pakistan Penal Code defines criminal offenses."},
        {"id": 2, "text": "The Constitution of Pakistan guarantees fundamental rights."},
        {"id": 3, "text": "Civil procedure code governs civil litigation."}
    ]
    results = vector_search("criminal law", docs)
    print(json.dumps(results, indent=2))
