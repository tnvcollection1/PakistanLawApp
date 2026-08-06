#!/usr/bin/env python3
"""
Ingest all scraped PLS data into MongoDB
"""
import os
import json
from pymongo import MongoClient
from datetime import datetime

def main():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = 'pls_database'
    
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    print(f"=== Ingesting data into MongoDB ({db_name}) ===")
    
    # 1. Case Laws (IDs only for now)
    print("\n1. Ingesting Case Law IDs...")
    with open('/app/backend/complete_caselist.json') as f:
        case_ids = json.load(f)
    
    # Convert to documents
    case_docs = [{'case_id': cid, 'scraped_at': datetime.utcnow()} for cid in case_ids]
    
    db.caselaws.drop()
    result = db.caselaws.insert_many(case_docs)
    print(f"   Inserted: {len(result.inserted_ids)} case law IDs")
    
    # 2. Legal Terms
    print("\n2. Ingesting Legal Terms...")
    with open('/app/backend/pls_legal_terms.json') as f:
        legal_terms = json.load(f)
    
    db.legal_terms.drop()
    if legal_terms['items']:
        result = db.legal_terms.insert_many(legal_terms['items'])
        print(f"   Inserted: {len(result.inserted_ids)} legal terms")
    
    # 3. Words & Phrases
    print("\n3. Ingesting Words & Phrases...")
    with open('/app/backend/pls_words_phrases.json') as f:
        words_phrases = json.load(f)
    
    db.words_phrases.drop()
    if words_phrases['items']:
        result = db.words_phrases.insert_many(words_phrases['items'])
        print(f"   Inserted: {len(result.inserted_ids)} words/phrases")
    
    # 4. Maxims
    print("\n4. Ingesting Maxims...")
    with open('/app/backend/pls_maxims.json') as f:
        maxims = json.load(f)
    
    db.maxims.drop()
    if maxims['items']:
        result = db.maxims.insert_many(maxims['items'])
        print(f"   Inserted: {len(result.inserted_ids)} maxims")
    
    # 5. Articles
    print("\n5. Ingesting Articles...")
    with open('/app/backend/pls_articles_with_content.json') as f:
        articles = json.load(f)
    
    db.articles.drop()
    if articles['articles']:
        result = db.articles.insert_many(articles['articles'])
        print(f"   Inserted: {len(result.inserted_ids)} articles")
    
    # 6. Topics
    print("\n6. Ingesting Topics...")
    with open('/app/backend/pls_topics.json') as f:
        topics = json.load(f)
    
    db.topics.drop()
    if topics['topics']:
        result = db.topics.insert_many(topics['topics'])
        print(f"   Inserted: {len(result.inserted_ids)} topics")
    
    # 7. Dictionary
    print("\n7. Ingesting Dictionary...")
    with open('/app/backend/pls_dictionary.json') as f:
        dictionary = json.load(f)
    
    db.dictionary.drop()
    if dictionary['items']:
        result = db.dictionary.insert_many(dictionary['items'])
        print(f"   Inserted: {len(result.inserted_ids)} dictionary items")
    
    # Create indexes
    print("\n=== Creating indexes ===")
    db.caselaws.create_index('case_id', unique=True)
    db.legal_terms.create_index('casetypeid')
    db.legal_terms.create_index('name')
    db.words_phrases.create_index('name')
    db.articles.create_index('article_id')
    db.articles.create_index('title')
    db.dictionary.create_index('word')
    print("   Indexes created")
    
    # Summary
    print("\n=== SUMMARY ===")
    for coll_name in db.list_collection_names():
        count = db[coll_name].count_documents({})
        print(f"   {coll_name}: {count:,} documents")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
