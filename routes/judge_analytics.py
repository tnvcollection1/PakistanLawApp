# Judge Analytics Route
from flask import Blueprint, jsonify, request
from datetime import datetime

judge_analytics_bp = Blueprint('judge_analytics', __name__)

@judge_analytics_bp.route('/analytics/judges', methods=['GET'])
def get_judge_stats():
    """Get judge statistics"""
    return jsonify({
        'judges': [
            {
                'name': 'Justice Example',
                'court': 'Supreme Court',
                'cases_count': 150,
                'decision_rate': 0.85,
                'avg_case_duration': 180
            }
        ],
        'summary': {
            'total_judges': 1,
            'total_cases': 150,
            'avg_decision_rate': 0.85
        }
    })

@judge_analytics_bp.route('/analytics/judge/<name>', methods=['GET'])
def get_judge_detail(name):
    """Get detailed analytics for a specific judge"""
    return jsonify({
        'name': name,
        'cases': [
            {'title': 'Case 1', 'citation': '2024 SCMR 1', 'decision': 'Allowed'},
            {'title': 'Case 2', 'citation': '2024 SCMR 2', 'decision': 'Dismissed'}
        ],
        'statistics': {
            'total_cases': 150,
            'allowed': 100,
            'dismissed': 50,
            'allowance_rate': 0.67
        }
    })

@judge_analytics_bp.route('/analytics/courts', methods=['GET'])
def get_court_stats():
    """Get court-level statistics"""
    return jsonify({
        'courts': [
            {
                'name': 'Supreme Court',
                'case_count': 1000,
                'pending': 200,
                'resolved': 800
            },
            {
                'name': 'High Court',
                'case_count': 5000,
                'pending': 1500,
                'resolved': 3500
            }
        ]
    })
