from flask import Blueprint, jsonify, request, current_app
from backend.services.pls_data import PLSDataService
from backend.utils.auth import require_auth, require_admin
from backend.utils.decorators import rate_limit, cache_response
from backend.utils.error_handlers import handle_api_error

pls_bp = Blueprint('pls', __name__, url_prefix='/api/v1/pls')
pls_service = PLSDataService()

@pls_bp.route('/statutes', methods=['GET'])
@cache_response(timeout=300)
@handle_api_error
def get_statutes():
    """Get all PLS statutes"""
    category = request.args.get('category')
    year = request.args.get('year', type=int)
    
    statutes = pls_service.get_statutes(category=category, year=year)
    return jsonify({
        'success': True,
        'data': statutes,
        'total': len(statutes)
    })

@pls_bp.route('/statutes/<string:statute_id>', methods=['GET'])
@cache_response(timeout=300)
@handle_api_error
def get_statute(statute_id):
    """Get a specific PLS statute"""
    statute = pls_service.get_statute_by_id(statute_id)
    if not statute:
        return jsonify({
            'success': False,
            'error': 'Statute not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': statute
    })

@pls_bp.route('/search', methods=['GET'])
@rate_limit(requests=30, window=60)
@handle_api_error
def search_statutes():
    """Search PLS statutes"""
    query = request.args.get('q', '')
    category = request.args.get('category')
    year = request.args.get('year', type=int)
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Search query is required'
        }), 400
    
    results = pls_service.search_statutes(query, category=category, year=year)
    return jsonify({
        'success': True,
        'data': results,
        'total': len(results),
        'query': query
    })

@pls_bp.route('/categories', methods=['GET'])
@cache_response(timeout=600)
@handle_api_error
def get_categories():
    """Get all PLS categories"""
    categories = pls_service.get_categories()
    return jsonify({
        'success': True,
        'data': categories
    })

@pls_bp.route('/years', methods=['GET'])
@cache_response(timeout=600)
@handle_api_error
def get_years():
    """Get all available years"""
    years = pls_service.get_years()
    return jsonify({
        'success': True,
        'data': years
    })

@pls_bp.route('/statutes/<string:statute_id>/download', methods=['GET'])
@require_auth
@handle_api_error
def download_statute(statute_id):
    """Download a statute document"""
    statute = pls_service.get_statute_by_id(statute_id)
    if not statute:
        return jsonify({
            'success': False,
            'error': 'Statute not found'
        }), 404
    
    # Implementation would generate and return PDF
    return jsonify({
        'success': True,
        'message': 'Download functionality to be implemented',
        'statute_id': statute_id
    })

@pls_bp.route('/statutes', methods=['POST'])
@require_admin
@rate_limit(requests=10, window=60)
@handle_api_error
def create_statute():
    """Create a new PLS statute (Admin only)"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({
            'success': False,
            'error': 'Title is required'
        }), 400
    
    statute = pls_service.create_statute(data)
    return jsonify({
        'success': True,
        'data': statute,
        'message': 'Statute created successfully'
    }), 201

@pls_bp.route('/statutes/<string:statute_id>', methods=['PUT'])
@require_admin
@rate_limit(requests=10, window=60)
@handle_api_error
def update_statute(statute_id):
    """Update a PLS statute (Admin only)"""
    data = request.get_json()
    
    statute = pls_service.update_statute(statute_id, data)
    if not statute:
        return jsonify({
            'success': False,
            'error': 'Statute not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': statute,
        'message': 'Statute updated successfully'
    })

@pls_bp.route('/statutes/<string:statute_id>', methods=['DELETE'])
@require_admin
@rate_limit(requests=10, window=60)
@handle_api_error
def delete_statute(statute_id):
    """Delete a PLS statute (Admin only)"""
    success = pls_service.delete_statute(statute_id)
    if not success:
        return jsonify({
            'success': False,
            'error': 'Statute not found'
        }), 404
    
    return jsonify({
        'success': True,
        'message': 'Statute deleted successfully'
    })

@pls_bp.route('/sync', methods=['POST'])
@require_admin
@handle_api_error
def sync_data():
    """Sync PLS data with external sources (Admin only)"""
    result = pls_service.sync_data()
    return jsonify({
        'success': True,
        'data': result,
        'message': 'Data sync initiated'
    })
