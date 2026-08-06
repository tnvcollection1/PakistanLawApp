"""
Notifications - Routes for notification management
"""
from flask import Blueprint, jsonify, request
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

NOTIFICATIONS = [
    {"id": 1, "title": "New case available", "message": "A new Supreme Court case has been added", "read": False, "created_at": "2024-01-01T00:00:00Z"},
    {"id": 2, "title": "System update", "message": "New features have been added to the platform", "read": True, "created_at": "2024-01-02T00:00:00Z"},
]

@notifications_bp.route('/api/notifications', methods=['GET'])
def list_notifications():
    return jsonify({"notifications": NOTIFICATIONS})

@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_read(notification_id):
    for n in NOTIFICATIONS:
        if n['id'] == notification_id:
            n['read'] = True
            return jsonify(n)
    return jsonify({"error": "Not found"}), 404
