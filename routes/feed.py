# Feed Route
from flask import Blueprint, jsonify
from datetime import datetime

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/feed', methods=['GET'])
def get_feed():
    """Get activity feed"""
    feed = {
        'timestamp': datetime.now().isoformat(),
        'items': [
            {
                'type': 'case_added',
                'title': 'New Supreme Court Case Added',
                'description': 'A new constitutional petition has been added to the database',
                'timestamp': datetime.now().isoformat()
            },
            {
                'type': 'statute_updated',
                'title': 'Statute Updated',
                'description': 'Pakistan Penal Code amendments have been incorporated',
                'timestamp': datetime.now().isoformat()
            }
        ]
    }
    return jsonify(feed)

@feed_bp.route('/feed/recent', methods=['GET'])
def get_recent_feed():
    """Get recent feed items"""
    return jsonify({
        'items': [
            {'type': 'case', 'count': 15, 'period': '24h'},
            {'type': 'statute', 'count': 3, 'period': '24h'}
        ]
    })
