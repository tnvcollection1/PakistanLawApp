"""
Feed - Routes for activity feed
"""
from flask import Blueprint, jsonify
from datetime import datetime

feed_bp = Blueprint('feed', __name__)

FEED_ITEMS = [
    {"id": 1, "type": "new_case", "title": "New Supreme Court Case", "description": "A new case has been added", "created_at": "2024-01-01T00:00:00Z"},
    {"id": 2, "type": "update", "title": "Statute Updated", "description": "A statute has been updated", "created_at": "2024-01-02T00:00:00Z"},
    {"id": 3, "type": "feature", "title": "New Feature", "description": "AI summaries are now available", "created_at": "2024-01-03T00:00:00Z"},
]

@feed_bp.route('/api/feed', methods=['GET'])
def get_feed():
    return jsonify({"feed": FEED_ITEMS})

@feed_bp.route('/api/feed/recent', methods=['GET'])
def get_recent_feed():
    return jsonify({"feed": FEED_ITEMS[:5]})
