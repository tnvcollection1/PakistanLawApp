"""
Notes - Routes for notes management
"""
from flask import Blueprint, jsonify, request
from datetime import datetime

notes_bp = Blueprint('notes', __name__)

NOTES = [
    {"id": 1, "user_id": 1, "case_id": "case-1", "content": "Important precedent", "created_at": "2024-01-01T00:00:00Z"},
    {"id": 2, "user_id": 1, "case_id": "case-2", "content": "Key citation", "created_at": "2024-01-02T00:00:00Z"},
]

@notes_bp.route('/api/notes', methods=['GET'])
def list_notes():
    return jsonify({"notes": NOTES})

@notes_bp.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    note = {
        "id": len(NOTES) + 1,
        "user_id": data.get('user_id'),
        "case_id": data.get('case_id'),
        "content": data.get('content'),
        "created_at": datetime.utcnow().isoformat(),
    }
    NOTES.append(note)
    return jsonify(note), 201

@notes_bp.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    global NOTES
    NOTES = [n for n in NOTES if n['id'] != note_id]
    return jsonify({"message": "Note deleted"})
