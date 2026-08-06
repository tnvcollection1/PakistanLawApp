"""
Data Cleaning - Routes for data cleaning and normalization
"""
from flask import Blueprint, jsonify, request

data_cleaning_bp = Blueprint('data_cleaning', __name__)

@data_cleaning_bp.route('/api/clean/normalize', methods=['POST'])
def normalize_text():
    data = request.get_json()
    text = data.get('text', '')
    # Normalize whitespace, punctuation, etc.
    cleaned = ' '.join(text.split())
    return jsonify({
        "original_length": len(text),
        "cleaned_length": len(cleaned),
        "text": cleaned,
    })

@data_cleaning_bp.route('/api/clean/deduplicate', methods=['POST'])
def deduplicate():
    data = request.get_json()
    items = data.get('items', [])
    seen = set()
    unique = []
    for item in items:
        key = item.get('title', '') + item.get('content', '')
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return jsonify({
        "original_count": len(items),
        "unique_count": len(unique),
        "duplicates_removed": len(items) - len(unique),
    })
