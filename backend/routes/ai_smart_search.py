from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.models.models import Case
from backend.services.ai_search import ai_smart_search
from backend.utils.decorators import require_auth

ai_smart_search_bp = Blueprint('ai_smart_search', __name__)

@ai_smart_search_bp.route('/api/ai/smart-search', methods=['POST'])
@require_auth
def smart_search():
    data = request.get_json()
    query = data.get('query', '')
    filters = data.get('filters', {})
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    results = ai_smart_search(query, filters)
    return jsonify({'results': [r.to_dict() for r in results]})

@ai_smart_search_bp.route('/api/ai/suggest', methods=['POST'])
@require_auth
def suggest():
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    suggestions = ai_smart_search.get_suggestions(query)
    return jsonify({'suggestions': suggestions})
