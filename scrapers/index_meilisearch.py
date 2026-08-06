"""
Index Meilisearch - Index documents into Meilisearch
"""
import json
import os
from meilisearch import Client

MEILI_URL = os.environ.get('MEILI_URL', 'http://localhost:7700')
MEILI_KEY = os.environ.get('MEILI_KEY', 'masterKey')

def index_documents(documents, index_name='cases'):
    client = Client(MEILI_URL, MEILI_KEY)
    index = client.index(index_name)
    response = index.add_documents(documents)
    print(f"Indexed {len(documents)} documents: {response}")
    return response

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python index_meilisearch.py <documents.json>")
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        documents = json.load(f)
    index_documents(documents)
