#!/usr/bin/env python3
"""Smart ID generator for cases and legal documents"""

import hashlib
import re

def generate_case_id(citation, date, title):
    """Generate a unique case ID from citation, date and title"""
    normalized = f"{citation}|{date}|{title}".lower()
    normalized = re.sub(r'[^\w|]', '', normalized)
    hash_obj = hashlib.md5(normalized.encode())
    return f"case_{hash_obj.hexdigest()[:12]}"

def generate_statute_id(title, year, section=None):
    """Generate a unique statute ID"""
    normalized = f"{title}|{year}".lower()
    if section:
        normalized += f"|{section}"
    hash_obj = hashlib.md5(normalized.encode())
    return f"statute_{hash_obj.hexdigest()[:12]}"

def generate_document_id(content, source_url=None):
    """Generate a unique document ID from content"""
    normalized = content[:500].lower().strip()
    if source_url:
        normalized = f"{source_url}|{normalized}"
    hash_obj = hashlib.md5(normalized.encode())
    return f"doc_{hash_obj.hexdigest()[:12]}"

def main():
    # Example usage
    case_id = generate_case_id("2024 SCMR 123", "2024-01-15", "Sample Case")
    print(f"Case ID: {case_id}")
    
    statute_id = generate_statute_id("Pakistan Penal Code", "1860", "Section 302")
    print(f"Statute ID: {statute_id}")

if __name__ == '__main__':
    main()
