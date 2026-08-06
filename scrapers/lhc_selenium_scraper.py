#!/usr/bin/env python3
"""
Lahore High Court Scraper using Selenium with undetected-chromedriver
Bypasses Cloudflare protection to fetch judgments from caselaw.lhc.gov.pk
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import os
import time
import re
from datetime import datetime

# Configuration
OUTPUT_DIR = '/tmp/lhc_data'
STATE_FILE = f'{OUTPUT_DIR}/lhc_state.json'
BATCH_SIZE = 50
BASE_URL = 'https://caselaw.lhc.gov.pk'

os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

def create_driver():
    """Create an undetected Chrome driver for server environment"""
    options = uc.ChromeOptions()
    
    # Essential for headless server
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Prevent crashes
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-translate')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--mute-audio')
    options.add_argument('--no-first-run')
    options.add_argument('--safebrowsing-disable-auto-update')
    
    # Memory optimization
    options.add_argument('--single-process')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-setuid-sandbox')
    
    # Window size
    options.add_argument('--window-size=1920,1080')
    
    # Use temp dirs with plenty of space
    options.add_argument('--user-data-dir=/tmp/chrome_user_data')
    options.add_argument('--disk-cache-dir=/tmp/chrome_cache')
    
    try:
        driver = uc.Chrome(options=options, version_main=146)
        driver.set_page_load_timeout(60)
        return driver
    except Exception as e:
        log(f'Failed to create driver: {e}')
        raise

def load_state():
    """Load scraper state from file"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'fetched_ids': [], 'page': 1, 'total_fetched': 0}

def save_state(state):
    """Save scraper state to file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def test_cloudflare_bypass():
    """Test if we can bypass Cloudflare protection"""
    log('Testing Cloudflare bypass...')
    driver = None
    try:
        driver = create_driver()
        log('Chrome driver created successfully')
        
        log(f'Navigating to {BASE_URL}...')
        driver.get(BASE_URL)
        log('Initial page load complete')
        
        time.sleep(8)  # Wait for Cloudflare challenge
        
        # Check if we got past Cloudflare
        page_source = driver.page_source.lower()
        title = driver.title.lower()
        current_url = driver.current_url
        
        log(f'Current URL: {current_url}')
        log(f'Page title: {driver.title}')
        
        if 'just a moment' in title or 'checking your browser' in page_source:
            log('Cloudflare challenge detected, waiting...')
            # Wait longer for challenge to complete
            time.sleep(15)
            page_source = driver.page_source.lower()
            title = driver.title.lower()
        
        if 'just a moment' in title or 'cloudflare' in title:
            log('ERROR: Cloudflare bypass FAILED - still on challenge page')
            return False, driver
        
        if '403' in driver.title or 'forbidden' in driver.title.lower():
            log('ERROR: Got 403 Forbidden')
            return False, driver
            
        log(f'SUCCESS! Bypassed Cloudflare')
        return True, driver
        
    except Exception as e:
        log(f'ERROR during test: {e}')
        import traceback
        traceback.print_exc()
        if driver:
            try:
                driver.quit()
            except:
                pass
        return False, None

def main():
    log('=' * 60)
    log('LAHORE HIGH COURT SELENIUM SCRAPER')
    log('=' * 60)
    
    # Clean up old chrome data
    import shutil
    for d in ['/tmp/chrome_user_data', '/tmp/chrome_cache']:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    
    # Test Cloudflare bypass first
    success, driver = test_cloudflare_bypass()
    
    if not success:
        log('Cloudflare bypass failed.')
        if driver:
            log(f'Final page source preview:')
            log(driver.page_source[:1000])
            driver.quit()
        return
    
    try:
        # Print page source for debugging
        log('Page loaded successfully!')
        log(f'Page source length: {len(driver.page_source)} chars')
        log(f'Page source preview:')
        log(driver.page_source[:800])
        
        # Explore the site structure
        log('\nExploring site structure...')
        
        # Find all links on the page
        links = driver.find_elements(By.TAG_NAME, 'a')
        log(f'Found {len(links)} links on homepage')
        
        unique_links = set()
        for link in links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()[:50] if link.text else ''
                if href and href.startswith('http'):
                    unique_links.add((text, href))
            except:
                continue
        
        log(f'\nUnique links found:')
        for text, href in list(unique_links)[:30]:
            log(f'  {text or "[no text]"} -> {href}')
        
        # Take a screenshot for debugging
        try:
            driver.save_screenshot(f'{OUTPUT_DIR}/lhc_homepage.png')
            log(f'\nScreenshot saved to {OUTPUT_DIR}/lhc_homepage.png')
        except Exception as e:
            log(f'Could not save screenshot: {e}')
        
    except Exception as e:
        log(f'Error during exploration: {e}')
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            log('Driver closed')

if __name__ == '__main__':
    main()
