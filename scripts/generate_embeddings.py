#!/usr/bin/env python3
"""Generate embeddings for legal documents"""

import json
import os
from sentence_transformers import SentenceTransformer

def load_model(model_name='all-MiniLM-L6-v2'):
    """Load sentence transformer model"""
    return SentenceTransformer(model_name)

def generate_embeddings(texts, model=None):
    """Generate embeddings for a list of texts"""
    if model is None:
        model = load_model()
    
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings

def process_cases(cases_file='all_cases.json', output_file='case_embeddings.json'):
    """Generate embeddings for all cases"""
    with open(cases_file, 'r') as f:
        cases = json.load(f)
    
    texts = []
    for case in cases:
        text = f"{case.get('title', '')} {case.get('content', '')}"
        texts.append(text)
    
    model = load_model()
    embeddings = generate_embeddings(texts, model)
    
    # Save embeddings
    embedding_data = []
    for i, case in enumerate(cases):
        embedding_data.append({
            'case_id': case.get('id', i),
            'embedding': embeddings[i].tolist()
        })
    
    with open(output_file, 'w') as f:
        json.dump(embedding_data, f, indent=2)
    
    print(f"Generated embeddings for {len(cases)} cases")

def search_similar(query, embeddings_file='case_embeddings.json', top_k=5):
    """Search for similar cases using embeddings"""
    import numpy as np
    
    with open(embeddings_file, 'r') as f:
        data = json.load(f)
    
    model = load_model()
    query_embedding = model.encode([query])[0]
    
    similarities = []
    for item in data:
        embedding = np.array(item['embedding'])
        similarity = np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
        similarities.append((item['case_id'], similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

def main():
    process_cases()

if __name__ == '__main__':
    main()
