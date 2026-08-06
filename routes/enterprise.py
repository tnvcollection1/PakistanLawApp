"""
Enterprise API Routes for Pakistan Law App
Provides enterprise-grade features for legal firms and organizations.
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
import jwt
import os

enterprise_bp = Blueprint('enterprise', __name__, url_prefix='/api/enterprise')

# Mock enterprise data (replace with database)
enterprise_users = {}
enterprise_organizations = {}
enterprise_plans = {
    'basic': {
        'name': 'Basic',
        'max_users': 5,
        'max_cases_per_month': 100,
        'features': ['search', 'basic_analytics', 'email_support']
    },
    'professional': {
        'name': 'Professional',
        'max_users': 25,
        'max_cases_per_month': 500,
        'features': ['search', 'advanced_analytics', 'api_access', 'priority_support', 'custom_reports']
    },
    'enterprise': {
        'name': 'Enterprise',
        'max_users': 100,
        'max_cases_per_month': 2000,
        'features': ['search', 'advanced_analytics', 'api_access', 'priority_support', 'custom_reports', 'dedicated_server', 'custom_integration']
    }
}


def enterprise_auth_required(f):
    """Decorator for enterprise authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        try:
            token = token.replace('Bearer ', '')
            payload = jwt.decode(token, os.getenv('JWT_SECRET', 'secret'), algorithms=['HS256'])
            g.enterprise_id = payload.get('enterprise_id')
            g.user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def check_plan_limit(limit_type):
    """Decorator to check plan limits."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            enterprise_id = g.get('enterprise_id')
            if not enterprise_id:
                return jsonify({'error': 'Enterprise ID required'}), 400
            
            org = enterprise_organizations.get(enterprise_id)
            if not org:
                return jsonify({'error': 'Organization not found'}), 404
            
            plan = enterprise_plans.get(org.get('plan', 'basic'))
            if not plan:
                return jsonify({'error': 'Invalid plan'}), 400
            
            # Check specific limits
            if limit_type == 'users':
                current_users = len(org.get('users', []))
                if current_users >= plan['max_users']:
                    return jsonify({'error': 'User limit reached'}), 403
            
            elif limit_type == 'cases':
                current_month = datetime.now().strftime('%Y-%m')
                monthly_cases = org.get('monthly_usage', {}).get(current_month, 0)
                if monthly_cases >= plan['max_cases_per_month']:
                    return jsonify({'error': 'Monthly case limit reached'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@enterprise_bp.route('/register', methods=['POST'])
def register_organization():
    """Register a new enterprise organization."""
    data = request.get_json()
    
    required_fields = ['name', 'email', 'plan']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate plan
    if data['plan'] not in enterprise_plans:
        return jsonify({'error': 'Invalid plan'}), 400
    
    org_id = f"org_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(enterprise_organizations)}"
    
    organization = {
        'id': org_id,
        'name': data['name'],
        'email': data['email'],
        'plan': data['plan'],
        'users': [],
        'created_at': datetime.now().isoformat(),
        'status': 'active',
        'billing': {
            'last_billed': None,
            'next_bill': (datetime.now() + timedelta(days=30)).isoformat()
        },
        'monthly_usage': {},
        'settings': {
            'api_access': data['plan'] in ['professional', 'enterprise'],
            'custom_reports': data['plan'] in ['professional', 'enterprise'],
            'dedicated_support': data['plan'] == 'enterprise'
        }
    }
    
    enterprise_organizations[org_id] = organization
    
    return jsonify({
        'message': 'Organization registered successfully',
        'organization': organization
    }), 201


@enterprise_bp.route('/organizations', methods=['GET'])
@enterprise_auth_required
def get_organizations():
    """Get all organizations (admin only)."""
    orgs = list(enterprise_organizations.values())
    return jsonify({'organizations': orgs}), 200


@enterprise_bp.route('/organization/<org_id>', methods=['GET'])
@enterprise_auth_required
def get_organization(org_id):
    """Get organization details."""
    org = enterprise_organizations.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify({'organization': org}), 200


@enterprise_bp.route('/organization/<org_id>/users', methods=['POST'])
@enterprise_auth_required
@check_plan_limit('users')
def add_user(org_id):
    """Add a user to organization."""
    data = request.get_json()
    
    if not data.get('email') or not data.get('name'):
        return jsonify({'error': 'Email and name are required'}), 400
    
    org = enterprise_organizations.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(org['users'])}"
    
    user = {
        'id': user_id,
        'name': data['name'],
        'email': data['email'],
        'role': data.get('role', 'member'),
        'created_at': datetime.now().isoformat(),
        'status': 'active'
    }
    
    org['users'].append(user)
    enterprise_users[user_id] = user
    
    return jsonify({
        'message': 'User added successfully',
        'user': user
    }), 201


@enterprise_bp.route('/organization/<org_id>/users', methods=['GET'])
@enterprise_auth_required
def get_users(org_id):
    """Get all users in organization."""
    org = enterprise_organizations.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify({'users': org.get('users', [])}), 200


@enterprise_bp.route('/usage', methods=['GET'])
@enterprise_auth_required
def get_usage():
    """Get enterprise usage statistics."""
    enterprise_id = g.get('enterprise_id')
    org = enterprise_organizations.get(enterprise_id)
    
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    current_month = datetime.now().strftime('%Y-%m')
    monthly_usage = org.get('monthly_usage', {}).get(current_month, 0)
    
    plan = enterprise_plans.get(org['plan'])
    usage_percentage = (monthly_usage / plan['max_cases_per_month'] * 100) if plan else 0
    
    return jsonify({
        'current_month': current_month,
        'monthly_usage': monthly_usage,
        'max_cases': plan['max_cases_per_month'] if plan else 0,
        'usage_percentage': round(usage_percentage, 2),
        'total_users': len(org.get('users', [])),
        'max_users': plan['max_users'] if plan else 0
    }), 200


@enterprise_bp.route('/analytics', methods=['GET'])
@enterprise_auth_required
def get_analytics():
    """Get enterprise analytics."""
    enterprise_id = g.get('enterprise_id')
    org = enterprise_organizations.get(enterprise_id)
    
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Generate mock analytics
    analytics = {
        'total_searches': 15420,
        'total_cases_viewed': 8932,
        'total_downloads': 2341,
        'active_users': len([u for u in org.get('users', []) if u.get('status') == 'active']),
        'search_trends': [
            {'date': '2024-01', 'searches': 1200},
            {'date': '2024-02', 'searches': 1350},
            {'date': '2024-03', 'searches': 1400}
        ],
        'popular_searches': [
            {'query': 'property rights', 'count': 234},
            {'query': 'criminal procedure', 'count': 198},
            {'query': 'constitutional law', 'count': 176}
        ],
        'court_distribution': [
            {'court': 'Supreme Court', 'percentage': 35},
            {'court': 'Lahore High Court', 'percentage': 25},
            {'court': 'Sindh High Court', 'percentage': 20}
        ]
    }
    
    return jsonify({'analytics': analytics}), 200


@enterprise_bp.route('/reports', methods=['POST'])
@enterprise_auth_required
def generate_report():
    """Generate custom report."""
    data = request.get_json()
    
    enterprise_id = g.get('enterprise_id')
    org = enterprise_organizations.get(enterprise_id)
    
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if custom reports are enabled
    if not org.get('settings', {}).get('custom_reports'):
        return jsonify({'error': 'Custom reports not available in current plan'}), 403
    
    report_type = data.get('type', 'usage')
    date_range = data.get('date_range', '30days')
    
    report = {
        'id': f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'type': report_type,
        'date_range': date_range,
        'generated_at': datetime.now().isoformat(),
        'status': 'generating',
        'url': f"/api/enterprise/reports/{report_type}"
    }
    
    return jsonify({
        'message': 'Report generation started',
        'report': report
    }), 202


@enterprise_bp.route('/settings', methods=['GET', 'PUT'])
@enterprise_auth_required
def manage_settings():
    """Get or update enterprise settings."""
    enterprise_id = g.get('enterprise_id')
    org = enterprise_organizations.get(enterprise_id)
    
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    if request.method == 'GET':
        return jsonify({'settings': org.get('settings', {})}), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        org['settings'].update(data)
        
        return jsonify({
            'message': 'Settings updated',
            'settings': org['settings']
        }), 200


@enterprise_bp.route('/billing', methods=['GET'])
@enterprise_auth_required
def get_billing_info():
    """Get billing information."""
    enterprise_id = g.get('enterprise_id')
    org = enterprise_organizations.get(enterprise_id)
    
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    plan = enterprise_plans.get(org['plan'])
    
    billing_info = {
        'plan': plan,
        'current_period_start': org.get('billing', {}).get('last_billed'),
        'current_period_end': org.get('billing', {}).get('next_bill'),
        'amount': calculate_billing_amount(org['plan']),
        'status': 'active'
    }
    
    return jsonify({'billing': billing_info}), 200


def calculate_billing_amount(plan):
    """Calculate billing amount based on plan."""
    prices = {
        'basic': 99,
        'professional': 299,
        'enterprise': 999
    }
    return prices.get(plan, 99)


@enterprise_bp.route('/support', methods=['POST'])
@enterprise_auth_required
def create_support_ticket():
    """Create a support ticket."""
    data = request.get_json()
    
    if not data.get('subject') or not data.get('description'):
        return jsonify({'error': 'Subject and description are required'}), 400
    
    ticket = {
        'id': f"ticket_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'subject': data['subject'],
        'description': data['description'],
        'priority': data.get('priority', 'medium'),
        'status': 'open',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'message': 'Support ticket created',
        'ticket': ticket
    }), 201


@enterprise_bp.route('/api-keys', methods=['GET', 'POST'])
@enterprise_auth_required
def manage_api_keys():
    """Manage API keys."""
    enterprise_id = g.get('enterprise_id')
    org = enterprise_organizations.get(enterprise_id)
    
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if API access is enabled
    if not org.get('settings', {}).get('api_access'):
        return jsonify({'error': 'API access not available in current plan'}), 403
    
    if request.method == 'GET':
        # Return existing API keys (mock)
        return jsonify({
            'api_keys': [
                {
                    'id': 'key_1',
                    'name': 'Production',
                    'created_at': datetime.now().isoformat(),
                    'last_used': datetime.now().isoformat()
                }
            ]
        }), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        
        new_key = {
            'id': f"key_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': data.get('name', 'New Key'),
            'key': f"pak_{os.urandom(24).hex()}",
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        return jsonify({
            'message': 'API key created',
            'api_key': new_key
        }), 201


@enterprise_bp.route('/audit-log', methods=['GET'])
@enterprise_auth_required
def get_audit_log():
    """Get audit log."""
    enterprise_id = g.get('enterprise_id')
    
    # Generate mock audit log
    audit_log = [
        {
            'id': 'audit_1',
            'action': 'user_login',
            'user': 'admin@example.com',
            'timestamp': datetime.now().isoformat(),
            'details': 'User logged in successfully'
        },
        {
            'id': 'audit_2',
            'action': 'search_performed',
            'user': 'user@example.com',
            'timestamp': datetime.now().isoformat(),
            'details': 'Search query: property rights'
        },
        {
            'id': 'audit_3',
            'action': 'case_downloaded',
            'user': 'user@example.com',
            'timestamp': datetime.now().isoformat(),
            'details': 'Case PLD 2023 SC 123 downloaded'
        }
    ]
    
    return jsonify({'audit_log': audit_log}), 200
