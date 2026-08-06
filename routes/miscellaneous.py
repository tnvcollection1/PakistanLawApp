from flask import Blueprint, jsonify

misc_bp = Blueprint('misc', __name__)

@misc_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

@misc_bp.route('/api/version', methods=['GET'])
def version():
    """Get API version."""
    return jsonify({'version': '1.0.0'})

@misc_bp.route('/api/ping', methods=['GET'])
def ping():
    """Simple ping endpoint."""
    return jsonify({'message': 'pong'})
