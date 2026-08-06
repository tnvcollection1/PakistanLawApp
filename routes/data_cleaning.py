# Data Cleaning Route
from flask import Blueprint, jsonify, request
import re

data_cleaning_bp = Blueprint('data_cleaning', __name__)

def clean_text(text):
    """Clean text data"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s\.\,\;\:\-\(\)]', '', text)
    return text.strip()

def normalize_citation(citation):
    """Normalize legal citation format"""
    # Remove extra spaces
    citation = re.sub(r'\s+', ' ', citation)
    # Standardize year format
    citation = re.sub(r'(\d{4})\s+([A-Z]+)', r'\1 \2', citation)
    return citation.strip()

@data_cleaning_bp.route('/clean/text', methods=['POST'])
def clean_text_endpoint():
    """Clean text data endpoint"""
    data = request.get_json()
    text = data.get('text', '')
    cleaned = clean_text(text)
    return jsonify({'original': text, 'cleaned': cleaned})

@data_cleaning_bp.route('/clean/citation', methods=['POST'])
def clean_citation_endpoint():
    """Clean citation endpoint"""
    data = request.get_json()
    citation = data.get('citation', '')
    cleaned = normalize_citation(citation)
    return jsonify({'original': citation, 'cleaned': cleaned})

@data_cleaning_bp.route('/clean/deduplicate', methods=['POST'])
def deduplicate():
    """Deduplicate list of items"""
    data = request.get_json()
    items = data.get('items', [])
    unique_items = list(set(items))
    return jsonify({
        'original_count': len(items),
        'unique_count': len(unique_items),
        'items': unique_items
    })
