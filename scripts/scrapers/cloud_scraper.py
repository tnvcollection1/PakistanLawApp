#!/usr/bin/env python3
"""Cloud-based scraper for Pakistan Legal System"""

import requests
import json
import boto3
from botocore.exceptions import ClientError
import time

class CloudScraper:
    def __init__(self, base_url="https://www.pakistanlawsite.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, endpoint, params=None):
        """Fetch a page from the website"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def upload_to_s3(self, data, bucket, key):
        """Upload data to S3 bucket"""
        try:
            s3 = boto3.client('s3')
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(data, indent=2)
            )
            print(f"Uploaded to s3://{bucket}/{key}")
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
    
    def scrape_and_store(self, endpoint, bucket, key):
        """Scrape data and store in cloud"""
        html = self.fetch_page(endpoint)
        if html:
            data = {'html': html, 'endpoint': endpoint, 'timestamp': time.time()}
            self.upload_to_s3(data, bucket, key)

def main():
    scraper = CloudScraper()
    scraper.scrape_and_store('cases', 'pakistan-law-data', 'cases/raw.json')

if __name__ == '__main__':
    main()
