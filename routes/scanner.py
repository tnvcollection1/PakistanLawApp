# Scanner Route
from flask import Blueprint, jsonify, request
import os
import subprocess

scanner_bp = Blueprint('scanner', __name__)

@scanner_bp.route('/scan', methods=['POST'])
def run_scan():
    """Run security scan on codebase"""
    scan_type = request.json.get('type', 'security')
    
    if scan_type == 'security':
        # Run bandit for Python security scan
        result = subprocess.run(['bandit', '-r', '.'], capture_output=True, text=True)
        return jsonify({
            'scan_type': scan_type,
            'output': result.stdout,
            'errors': result.stderr,
            'return_code': result.returncode
        })
    elif scan_type == 'dependencies':
        # Run safety check
        result = subprocess.run(['safety', 'check'], capture_output=True, text=True)
        return jsonify({
            'scan_type': scan_type,
            'output': result.stdout,
            'errors': result.stderr,
            'return_code': result.returncode
        })
    
    return jsonify({'error': 'Unknown scan type'}), 400

@scanner_bp.route('/scan/status', methods=['GET'])
def scan_status():
    """Get scan status"""
    return jsonify({
        'status': 'idle',
        'last_scan': None,
        'issues_found': 0
    })
