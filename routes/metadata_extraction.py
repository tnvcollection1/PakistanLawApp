from flask import Blueprint, jsonify, request
from db import get_db
import json

metadata_bp = Blueprint('metadata_extraction', __name__)

@metadata_bp.route('/api/extract_metadata', methods=['POST'])
def extract_metadata():
    data = request.json
    text = data.get('text', '')
    
    # Simple metadata extraction
    metadata = {
        "word_count": len(text.split()),
        "char_count": len(text),
        "has_citation": bool(any(c in text for c in ['PLD', 'SCMR', 'PCrLJ'])),
    }
    
    return jsonify(metadata)
