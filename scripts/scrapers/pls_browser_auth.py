#!/usr/bin/env python3
"""Browser authentication handler for PLS."""

import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://beta.pakistanlawsite.com"
COOKIES_FILE = Path("data/pls_cookies.json")

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)

def authenticate(username, password):
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/login")
        
        # Wait for and fill login form
        wait = WebDriverWait(driver, 20)
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        
        # Wait for login to complete
        wait.until(EC.url_contains("/dashboard"))
        
        # Get cookies
        cookies = driver.get_cookies()
        COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"Authentication successful. Cookies saved to {COOKIES_FILE}")
        return cookies
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None
    finally:
        driver.quit()

def load_cookies():
    if COOKIES_FILE.exists():
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Authenticate with PLS Beta')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='Password')
    args = parser.parse_args()
    
    authenticate(args.username, args.password)

if __name__ == '__main__':
    main()
