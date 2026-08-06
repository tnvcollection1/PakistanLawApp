from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.models.models import Journal
from backend.services.citation_service import CitationService
from backend.utils.decorators import require_auth

journals_bp = Blueprint('journals', __name__)
citation_service = CitationService()

@journals_bp.route('/api/journals', methods=['GET'])
def list_journals():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('q', '')
    query = Journal.query
    if search:
        query = query.filter(Journal.title.ilike(f'%{search}%'))
    journals = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [j.to_dict() for j in journals.items],
        'total': journals.total,
        'pages': journals.pages,
        'page': page
    })

@journals_bp.route('/api/journals/<int:id>', methods=['GET'])
def get_journal(id):
    journal = Journal.query.get_or_404(id)
    return jsonify(journal.to_dict())

@journals_bp.route('/api/journals/<int:id>/citations', methods=['GET'])
def get_journal_citations(id):
    journal = Journal.query.get_or_404(id)
    return jsonify(citation_service.get_citations_for_journal(journal))
