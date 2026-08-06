from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.models.models import Case
from backend.services.ai_search import ai_case_finder
from backend.utils.decorators import require_auth

ai_case_finder_bp = Blueprint('ai_case_finder', __name__)

@ai_case_finder_bp.route('/api/ai/case-finder', methods=['POST'])
@require_auth
def find_case():
    data = request.get_json()
    query = data.get('query', '')
    filters = data.get('filters', {})
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    results = ai_case_finder(query, filters)
    return jsonify({'results': [r.to_dict() for r in results]})

@ai_case_finder_bp.route('/api/ai/similar-cases', methods=['POST'])
@require_auth
def similar_cases():
    data = request.get_json()
    case_id = data.get('case_id')
    if not case_id:
        return jsonify({'error': 'Case ID is required'}), 400
    case = Case.query.get_or_404(case_id)
    results = ai_case_finder.find_similar(case)
    return jsonify({'results': [r.to_dict() for r in results]})
