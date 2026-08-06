import csv
import os
from pymongo import MongoClient

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'pakistanlaw')

def import_csv_to_mongo(csv_file_path, collection_name):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[collection_name]

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    if records:
        result = collection.insert_many(records)
        print(f"Inserted {len(result.inserted_ids)} records into {collection_name}")
    else:
        print("No records found in CSV")

    client.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python import_csv_to_mongo.py <csv_file> <collection_name>")
        sys.exit(1)
    import_csv_to_mongo(sys.argv[1], sys.argv[2])
