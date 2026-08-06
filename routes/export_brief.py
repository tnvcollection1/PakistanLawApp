# Export Brief Route
from flask import Blueprint, jsonify, request
import os

export_brief_bp = Blueprint('export_brief', __name__)

@export_brief_bp.route('/export/brief', methods=['POST'])
def export_brief():
    data = request.get_json()
    case_id = data.get('case_id')
    format_type = data.get('format', 'pdf')
    
    if not case_id:
        return jsonify({'error': 'case_id is required'}), 400
    
    # TODO: Implement brief export logic
    return jsonify({
        'status': 'success',
        'message': f'Brief export for case {case_id} in {format_type} format initiated'
    })
