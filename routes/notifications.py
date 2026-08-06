# Notifications Route
from flask import Blueprint, jsonify, request
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

# In-memory storage for demo
notifications = []

@notifications_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Get all notifications for the current user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    user_notifications = [n for n in notifications if n['user_id'] == user_id]
    return jsonify({'notifications': user_notifications})

@notifications_bp.route('/notifications', methods=['POST'])
def create_notification():
    """Create a new notification"""
    data = request.get_json()
    notification = {
        'id': len(notifications) + 1,
        'user_id': data.get('user_id'),
        'message': data.get('message'),
        'type': data.get('type', 'info'),
        'read': False,
        'created_at': datetime.now().isoformat()
    }
    notifications.append(notification)
    return jsonify(notification), 201

@notifications_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_read(notification_id):
    """Mark a notification as read"""
    for n in notifications:
        if n['id'] == notification_id:
            n['read'] = True
            return jsonify(n)
    return jsonify({'error': 'Notification not found'}), 404
