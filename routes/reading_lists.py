"""
Reading Lists - Routes for reading list management
"""
from flask import Blueprint, jsonify, request
from datetime import datetime

reading_lists_bp = Blueprint('reading_lists', __name__)

READING_LISTS = [
    {"id": 1, "user_id": 1, "name": "Important Cases", "cases": ["case-1", "case-2"], "created_at": "2024-01-01T00:00:00Z"},
    {"id": 2, "user_id": 1, "name": "Research", "cases": ["case-3"], "created_at": "2024-01-02T00:00:00Z"},
]

@reading_lists_bp.route('/api/reading-lists', methods=['GET'])
def list_reading_lists():
    return jsonify({"reading_lists": READING_LISTS})

@reading_lists_bp.route('/api/reading-lists', methods=['POST'])
def create_reading_list():
    data = request.get_json()
    reading_list = {
        "id": len(READING_LISTS) + 1,
        "user_id": data.get('user_id'),
        "name": data.get('name'),
        "cases": data.get('cases', []),
        "created_at": datetime.utcnow().isoformat(),
    }
    READING_LISTS.append(reading_list)
    return jsonify(reading_list), 201

@reading_lists_bp.route('/api/reading-lists/<int:list_id>', methods=['PUT'])
def update_reading_list(list_id):
    data = request.get_json()
    for rl in READING_LISTS:
        if rl['id'] == list_id:
            rl['name'] = data.get('name', rl['name'])
            rl['cases'] = data.get('cases', rl['cases'])
            return jsonify(rl)
    return jsonify({"error": "Not found"}), 404

@reading_lists_bp.route('/api/reading-lists/<int:list_id>', methods=['DELETE'])
def delete_reading_list(list_id):
    global READING_LISTS
    READING_LISTS = [rl for rl in READING_LISTS if rl['id'] != list_id]
    return jsonify({"message": "Reading list deleted"})
