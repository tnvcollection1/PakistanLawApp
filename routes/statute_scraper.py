from flask import Blueprint, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

statute_scraper_bp = Blueprint('statute_scraper', __name__)

@statute_scraper_bp.route('/api/scrape/statute', methods=['POST'])
def scrape_statute():
    """Scrape statute content from a URL."""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else 'Unknown'
        
        # Extract content
        content = soup.get_text()
        lines = (line.strip() for line in content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
        clean_content = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Look for act number and year
        act_number = None
        year = None
        
        patterns = [
            r'Act\s+(?:No\.?\s*)?(\d+)\s+of\s+(\d{4})',
            r'Ordinance\s+(?:No\.?\s*)?(\d+)\s+of\s+(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, resp.text, re.IGNORECASE)
            if match:
                act_number = match.group(1)
                year = int(match.group(2))
                break
        
        return jsonify({
            'url': url,
            'title': title_text,
            'act_number': act_number,
            'year': year,
            'content': clean_content[:50000],  # Limit content size
            'content_length': len(clean_content),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'url': url,
            'status': 'failed'
        }), 500

import re
