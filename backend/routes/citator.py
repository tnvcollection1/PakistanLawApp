from flask import Blueprint, jsonify, request
from services.citation_service import CitationService
from middleware.auth import token_required
from database.models import Case
import logging

logger = logging.getLogger(__name__)
citator_bp = Blueprint('citator', __name__)
citation_service = CitationService()

@citator_bp.route('/api/cases/<case_id>/citations', methods=['GET'])
@token_required
def get_case_citations(case_id):
    """Get all citations for a case."""
    try:
        citations = citation_service.get_citations(case_id)
        return jsonify({
            'success': True,
            'citations': citations
        })
    except Exception as e:
        logger.error(f"Error getting citations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@citator_bp.route('/api/cases/<case_id>/citing', methods=['GET'])
@token_required
def get_citing_cases(case_id):
    """Get cases that cite this case."""
    try:
        citing_cases = citation_service.get_citing_cases(case_id)
        return jsonify({
            'success': True,
            'citing_cases': citing_cases
        })
    except Exception as e:
        logger.error(f"Error getting citing cases: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@citator_bp.route('/api/cases/<case_id>/cited-by', methods=['GET'])
@token_required
def get_cited_by_cases(case_id):
    """Get cases cited by this case."""
    try:
        cited_cases = citation_service.get_cited_cases(case_id)
        return jsonify({
            'success': True,
            'cited_cases': cited_cases
        })
    except Exception as e:
        logger.error(f"Error getting cited cases: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@citator_bp.route('/api/cases/most-cited', methods=['GET'])
@token_required
def get_most_cited_cases():
    """Get most frequently cited cases."""
    try:
        limit = request.args.get('limit', 50, type=int)
        cases = citation_service.get_most_cited_cases(limit)
        return jsonify({
            'success': True,
            'cases': cases
        })
    except Exception as e:
        logger.error(f"Error getting most cited cases: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@citator_bp.route('/api/citations/analyze', methods=['POST'])
@token_required
def analyze_citations():
    """Analyze citations for given cases."""
    try:
        data = request.get_json()
        case_ids = data.get('case_ids', [])
        analysis = citation_service.analyze_citations(case_ids)
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        logger.error(f"Error analyzing citations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@citator_bp.route('/api/citations/build', methods=['POST'])
@token_required
def build_citation_network():
    """Build citation network for visualization."""    
    try:
        data = request.get_json()
        case_ids = data.get('case_ids', [])
        network = citation_service.build_citation_network(case_ids)
        return jsonify({
            'success': True,
            'network': network
        })
    except Exception as e:
        logger.error(f"Error building citation network: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
