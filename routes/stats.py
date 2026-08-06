from flask import Blueprint, jsonify
from models import Case
from extensions import db

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """Get general statistics about the cases."""
    total_cases = Case.query.count()
    total_with_content = Case.query.filter(Case.content.isnot(None)).count()
    total_without_content = total_cases - total_with_content
    
    return jsonify({
        'total_cases': total_cases,
        'total_with_content': total_with_content,
        'total_without_content': total_without_content
    })

@stats_bp.route('/api/stats/courts', methods=['GET'])
def get_court_stats():
    """Get case counts by court."""
    from sqlalchemy import func
    
    court_counts = db.session.query(
        Case.court,
        func.count(Case.id)
    ).group_by(Case.court).all()
    
    return jsonify({
        'court_counts': [
            {'court': court, 'count': count}
            for court, count in court_counts
        ]
    })

@stats_bp.route('/api/stats/years', methods=['GET'])
def get_year_stats():
    """Get case counts by year."""
    from sqlalchemy import func
    
    year_counts = db.session.query(
        Case.year,
        func.count(Case.id)
    ).group_by(Case.year).order_by(Case.year.desc()).all()
    
    return jsonify({
        'year_counts': [
            {'year': year, 'count': count}
            for year, count in year_counts
        ]
    })
