# Updates Route
from flask import Blueprint, jsonify
from datetime import datetime, timedelta

updates_bp = Blueprint('updates', __name__)

@updates_bp.route('/updates', methods=['GET'])
def get_updates():
    """Get recent updates and changes"""
    updates = {
        'last_update': datetime.now().isoformat(),
        'new_cases': 15,
        'updated_statutes': 3,
        'system_changes': [
            'Improved search algorithm',
            'New citation features',
            'Performance optimizations'
        ]
    }
    return jsonify(updates)

@updates_bp.route('/updates/recent', methods=['GET'])
def get_recent_updates():
    """Get updates from the last 7 days"""
    since = datetime.now() - timedelta(days=7)
    # TODO: Query database for recent updates
    return jsonify({
        'since': since.isoformat(),
        'updates': []
    })
