import faiss, json, os, numpy as np
from backend.embeddings import get_embedding
from backend.models.models import Case
from backend.extensions import db

def rebuild_faiss_index():
    print("[+] Rebuilding FAISS index...")
    cases = Case.query.filter(Case.embedding != None).all()
    if not cases:
        print("[-] No cases with embeddings found")
        return
    dim = len(cases[0].embedding)
    index = faiss.IndexFlatIP(dim)
    vectors = []
    ids = []
    for c in cases:
        vectors.append(c.embedding)
        ids.append(c.id)
    vectors = np.array(vectors, dtype='float32')
    index.add(vectors)
    os.makedirs('data', exist_ok=True)
    faiss.write_index(index, 'data/faiss.index')
    with open('data/faiss_ids.json', 'w') as f:
        json.dump(ids, f)
    print(f"[+] Index built with {len(ids)} vectors")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        rebuild_faiss_index()
