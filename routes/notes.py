# Notes Route
from flask import Blueprint, jsonify, request
from datetime import datetime

notes_bp = Blueprint('notes', __name__)

# In-memory storage for demo
notes_db = {}

@notes_bp.route('/notes', methods=['GET'])
def get_notes():
    """Get all notes for the current user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    user_notes = notes_db.get(user_id, [])
    return jsonify({'notes': user_notes})

@notes_bp.route('/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    note = {
        'id': len(notes_db.get(user_id, [])) + 1,
        'title': data.get('title', 'Untitled'),
        'content': data.get('content', ''),
        'case_id': data.get('case_id'),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    if user_id not in notes_db:
        notes_db[user_id] = []
    notes_db[user_id].append(note)
    
    return jsonify(note), 201

@notes_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update an existing note"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id or user_id not in notes_db:
        return jsonify({'error': 'Note not found'}), 404
    
    for note in notes_db[user_id]:
        if note['id'] == note_id:
            note['title'] = data.get('title', note['title'])
            note['content'] = data.get('content', note['content'])
            note['updated_at'] = datetime.now().isoformat()
            return jsonify(note)
    
    return jsonify({'error': 'Note not found'}), 404

@notes_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note"""
    user_id = request.args.get('user_id')
    if not user_id or user_id not in notes_db:
        return jsonify({'error': 'Note not found'}), 404
    
    notes_db[user_id] = [n for n in notes_db[user_id] if n['id'] != note_id]
    return jsonify({'message': 'Note deleted'})
