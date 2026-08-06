#!/usr/bin/env python3
"""Dual cloud scraper for redundant data collection"""

import requests
import json
import boto3
import time
from bs4 import BeautifulSoup

class DualCloudScraper:
    def __init__(self, base_url="https://www.pakistanlawsite.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.s3_client = boto3.client('s3')
        self.primary_bucket = 'pakistan-law-primary'
        self.secondary_bucket = 'pakistan-law-backup'
    
    def fetch_page(self, endpoint):
        """Fetch page from website"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def upload_to_both(self, key, data):
        """Upload data to both buckets"""
        json_data = json.dumps(data, indent=2)
        
        # Upload to primary
        try:
            self.s3_client.put_object(
                Bucket=self.primary_bucket,
                Key=key,
                Body=json_data
            )
            print(f"Uploaded to primary: {key}")
        except Exception as e:
            print(f"Error uploading to primary: {e}")
        
        # Upload to secondary
        try:
            self.s3_client.put_object(
                Bucket=self.secondary_bucket,
                Key=key,
                Body=json_data
            )
            print(f"Uploaded to secondary: {key}")
        except Exception as e:
            print(f"Error uploading to secondary: {e}")
    
    def scrape_and_backup(self, endpoint, key):
        """Scrape and backup to both clouds"""
        html = self.fetch_page(endpoint)
        if html:
            data = {
                'html': html,
                'endpoint': endpoint,
                'timestamp': time.time()
            }
            self.upload_to_both(key, data)

def main():
    scraper = DualCloudScraper()
    scraper.scrape_and_backup('cases', 'cases/raw.json')

if __name__ == '__main__':
    main()
