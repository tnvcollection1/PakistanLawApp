"""
Updates - Routes for update and changelog management
"""
from flask import Blueprint, jsonify
from datetime import datetime

updates_bp = Blueprint('updates', __name__)

UPDATES = [
    {"id": 1, "version": "1.0.0", "date": "2024-01-01", "changes": ["Initial release"]},
    {"id": 2, "version": "1.1.0", "date": "2024-02-01", "changes": ["Added AI summaries", "Improved search"]},
    {"id": 3, "version": "1.2.0", "date": "2024-03-01", "changes": ["Added citation analysis", "New UI"]},
]

@updates_bp.route('/api/updates', methods=['GET'])
def list_updates():
    return jsonify({"updates": UPDATES})

@updates_bp.route('/api/updates/latest', methods=['GET'])
def latest_update():
    return jsonify(UPDATES[-1] if UPDATES else {})
