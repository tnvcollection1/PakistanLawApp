from flask import Blueprint, jsonify, request
import re

urdu_bp = Blueprint('urdu', __name__)

# Basic Urdu text detection and transliteration helpers
URDU_RANGE = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'

def is_urdu_text(text):
    """Check if text contains Urdu characters."""
    return bool(re.search(URDU_RANGE, text))

def detect_language(text):
    """Detect if text is Urdu, English, or mixed."""
    urdu_chars = len(re.findall(URDU_RANGE, text))
    total_chars = len(text.strip())
    
    if total_chars == 0:
        return 'unknown'
    
    urdu_ratio = urdu_chars / total_chars
    
    if urdu_ratio > 0.5:
        return 'urdu'
    elif urdu_ratio > 0.1:
        return 'mixed'
    else:
        return 'english'

@urdu_bp.route('/api/detect-language', methods=['POST'])
def detect_language_endpoint():
    """Detect the language of submitted text."""
    data = request.get_json()
    text = data.get('text', '')
    
    return jsonify({
        'text': text,
        'language': detect_language(text),
        'has_urdu': is_urdu_text(text)
    })

@urdu_bp.route('/api/search/urdu', methods=['GET'])
def search_urdu():
    """Search with Urdu text support."""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    language = detect_language(query)
    
    # For now, return basic info about the query
    return jsonify({
        'query': query,
        'detected_language': language,
        'is_urdu': language in ('urdu', 'mixed'),
        'results': [],
        'message': 'Urdu search is under development'
    })

# Simple transliteration mapping (basic)
URDU_TO_ENGLISH = {
    'ا': 'a', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ٹ': 'tt',
    'ث': 's', 'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh',
    'د': 'd', 'ڈ': 'dd', 'ذ': 'z', 'ر': 'r', 'ڑ': 'rr',
    'ز': 'z', 'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
    'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh',
    'ف': 'f', 'ق': 'q', 'ک': 'k', 'گ': 'g', 'ل': 'l',
    'م': 'm', 'ن': 'n', 'ں': 'nn', 'و': 'o', 'ہ': 'h',
    'ھ': 'h', 'ی': 'y', 'ے': 'e',
}

def transliterate_urdu(text):
    """Basic transliteration from Urdu to English."""
    result = ''
    for char in text:
        result += URDU_TO_ENGLISH.get(char, char)
    return result

@urdu_bp.route('/api/transliterate', methods=['POST'])
def transliterate():
    """Transliterate Urdu text to English."""
    data = request.get_json()
    text = data.get('text', '')
    
    return jsonify({
        'original': text,
        'transliterated': transliterate_urdu(text),
        'method': 'basic_mapping'
    })
