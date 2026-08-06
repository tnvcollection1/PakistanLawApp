from flask import Blueprint, jsonify, request
from db import get_db
import requests
from bs4 import BeautifulSoup

statute_scraper_bp = Blueprint('statute_scraper', __name__)

@statute_scraper_bp.route('/api/scrape_statute', methods=['POST'])
def scrape_statute():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.find('title').get_text(strip=True) if soup.find('title') else 'No title'
        content = soup.get_text(separator='\n', strip=True)
        
        db = get_db()
        db.statutes.insert_one({"url": url, "title": title, "content": content[:5000]})
        
        return jsonify({"title": title, "content_length": len(content)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
