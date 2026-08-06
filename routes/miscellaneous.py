from flask import Blueprint, jsonify, request
from db import get_db

misc_bp = Blueprint('misc', __name__)

@misc_bp.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    db = get_db()
    results = db.judgments.find({"$text": {"$search": query}}).limit(50)
    return jsonify(list(results))

@misc_bp.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})
