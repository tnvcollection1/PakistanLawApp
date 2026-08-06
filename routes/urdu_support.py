from flask import Blueprint, jsonify, request
from db import get_db

urdu_bp = Blueprint('urdu', __name__)

@urdu_bp.route('/api/urdu/search', methods=['GET'])
def search_urdu():
    query = request.args.get('q', '')
    db = get_db()
    results = db.judgments.find({"urdu_text": {"$regex": query}}).limit(50)
    return jsonify(list(results))

@urdu_bp.route('/api/urdu/translate', methods=['POST'])
def translate_urdu():
    data = request.json
    text = data.get('text', '')
    # Placeholder for translation logic
    return jsonify({"original": text, "translated": text})
