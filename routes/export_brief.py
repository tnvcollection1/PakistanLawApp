"""
Export Brief - Routes for brief export functionality
"""
from flask import Blueprint, jsonify, request, send_file
import io
import json

export_brief_bp = Blueprint('export_brief', __name__)

@export_brief_bp.route('/api/export/brief', methods=['POST'])
def export_brief():
    data = request.get_json()
    case_ids = data.get('case_ids', [])
    format_type = data.get('format', 'pdf')
    brief = {
        "title": data.get('title', 'Untitled Brief'),
        "cases": case_ids,
        "format": format_type,
        "created_at": "2024-01-01T00:00:00Z",
    }
    return jsonify(brief)

@export_brief_bp.route('/api/export/brief/<brief_id>/download', methods=['GET'])
def download_brief(brief_id):
    # Generate a simple text file for download
    content = f"Brief {brief_id}\n\nThis is a placeholder brief."
    buffer = io.BytesIO(content.encode())
    buffer.seek(0)
    return send_file(buffer, mimetype='text/plain', as_attachment=True, download_name=f'brief-{brief_id}.txt')
