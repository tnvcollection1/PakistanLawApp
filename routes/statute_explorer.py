"""
Statute Explorer - Routes for statute exploration
"""
from flask import Blueprint, jsonify, request
import random

statute_explorer_bp = Blueprint('statute_explorer', __name__)

STATUTES = [
    {"id": "1", "title": "Pakistan Penal Code", "year": 1860, "chapters": 23},
    {"id": "2", "title": "Code of Criminal Procedure", "year": 1898, "chapters": 37},
    {"id": "3", "title": "Constitution of Pakistan", "year": 1973, "chapters": 14},
    {"id": "4", "title": "Civil Procedure Code", "year": 1908, "chapters": 10},
]

@statute_explorer_bp.route('/api/statutes', methods=['GET'])
def list_statutes():
    return jsonify({"statutes": STATUTES})

@statute_explorer_bp.route('/api/statutes/<statute_id>', methods=['GET'])
def get_statute(statute_id):
    statute = next((s for s in STATUTES if s['id'] == statute_id), None)
    if not statute:
        return jsonify({"error": "Statute not found"}), 404
    return jsonify(statute)

@statute_explorer_bp.route('/api/statutes/<statute_id>/chapters', methods=['GET'])
def get_chapters(statute_id):
    chapters = []
    for i in range(1, 6):
        chapters.append({
            "id": f"{statute_id}-ch{i}",
            "number": i,
            "title": f"Chapter {i}",
            "sections": random.randint(5, 30),
        })
    return jsonify({"chapters": chapters})

@statute_explorer_bp.route('/api/statutes/<statute_id>/chapters/<chapter_id>/sections', methods=['GET'])
def get_sections(statute_id, chapter_id):
    sections = []
    for i in range(1, 11):
        sections.append({
            "id": f"{chapter_id}-sec{i}",
            "number": i,
            "title": f"Section {i}",
            "content": f"This is the content of section {i}.",
        })
    return jsonify({"sections": sections})
