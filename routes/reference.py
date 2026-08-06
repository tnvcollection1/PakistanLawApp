from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.models.models import Case, Statute, Reference
from backend.utils.decorators import require_auth

reference_bp = Blueprint('reference', __name__)

@reference_bp.route('/api/references', methods=['GET'])
def list_references():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    refs = Reference.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [r.to_dict() for r in refs.items],
        'total': refs.total,
        'pages': refs.pages,
        'page': page
    })

@reference_bp.route('/api/cases/<int:id>/references', methods=['GET'])
def get_case_references(id):
    case = Case.query.get_or_404(id)
    refs = Reference.query.filter_by(source_case_id=id).all()
    return jsonify([r.to_dict() for r in refs])

@reference_bp.route('/api/statutes/<int:id>/references', methods=['GET'])
def get_statute_references(id):
    statute = Statute.query.get_or_404(id)
    refs = Reference.query.filter_by(source_statute_id=id).all()
    return jsonify([r.to_dict() for r in refs])
