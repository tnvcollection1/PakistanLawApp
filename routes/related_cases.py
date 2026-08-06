from flask import Blueprint, jsonify, request
from models import Case
from extensions import db
from sqlalchemy import func

related_bp = Blueprint('related', __name__)

@related_bp.route('/api/cases/<int:case_id>/related', methods=['GET'])
def get_related_cases(case_id):
    """Find related cases based on shared citations and content similarity."""
    case = Case.query.get_or_404(case_id)
    
    limit = request.args.get('limit', 5, type=int)
    
    # Find cases with same court and similar year
    court_cases = Case.query.filter(
        Case.court == case.court,
        Case.id != case_id
    ).order_by(
        func.abs(Case.year - case.year)
    ).limit(limit).all()
    
    # Find cases with shared citations (if citations field exists)
    related = []
    for c in court_cases:
        score = 0
        if c.court == case.court:
            score += 50
        if c.year == case.year:
            score += 30
        elif abs(c.year - case.year) <= 2:
            score += 15
        
        related.append({
            'id': c.id,
            'title': c.title,
            'citation': c.citation,
            'court': c.court,
            'year': c.year,
            'relevance_score': score
        })
    
    # Sort by relevance score
    related.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return jsonify({
        'case_id': case_id,
        'case_title': case.title,
        'related_cases': related[:limit]
    })

@related_bp.route('/api/cases/<int:case_id>/cited-by', methods=['GET'])
def get_cited_by(case_id):
    """Get cases that cite this case."""
    case = Case.query.get_or_404(case_id)
    
    # Simple citation matching - can be enhanced with proper citation parsing
    citation_pattern = case.citation.replace(' ', '%')
    
    citing_cases = Case.query.filter(
        Case.content.like(f'%{citation_pattern}%'),
        Case.id != case_id
    ).limit(10).all()
    
    return jsonify({
        'case_id': case_id,
        'citation': case.citation,
        'cited_by': [{
            'id': c.id,
            'title': c.title,
            'citation': c.citation,
            'court': c.court,
            'year': c.year
        } for c in citing_cases]
    })
