#!/usr/bin/env python3
"""Lawyer extractor v3"""

import requests
import json
import re
from bs4 import BeautifulSoup

def extract_lawyers_from_case(case_url):
    """Extract lawyer names from case page"""
    try:
        response = requests.get(case_url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        lawyers = {
            'appellants': [],
            'respondents': [],
            'counsel': []
        }
        
        # Extract appellants
        for elem in soup.find_all(text=re.compile(r'Appellant[s]?\s*[:\-]')):
            parent = elem.parent
            if parent:
                text = parent.text
                names = re.findall(r'[A-Z][a-zA-Z\s]+(?: Advocate| Counsel)', text)
                lawyers['appellants'].extend(names)
        
        # Extract respondents
        for elem in soup.find_all(text=re.compile(r'Respondent[s]?\s*[:\-]')):
            parent = elem.parent
            if parent:
                text = parent.text
                names = re.findall(r'[A-Z][a-zA-Z\s]+(?: Advocate| Counsel)', text)
                lawyers['respondents'].extend(names)
        
        # Extract counsel
        for elem in soup.find_all(text=re.compile(r'Counsel[s]?\s*[:\-]')):
            parent = elem.parent
            if parent:
                text = parent.text
                names = re.findall(r'[A-Z][a-zA-Z\s]+(?: Advocate| Counsel)', text)
                lawyers['counsel'].extend(names)
        
        return lawyers
    except Exception as e:
        return {'error': str(e)}

def main():
    url = "https://www.pakistanlawsite.com/case/sample"
    lawyers = extract_lawyers_from_case(url)
    print(json.dumps(lawyers, indent=2))

if __name__ == '__main__':
    main()
