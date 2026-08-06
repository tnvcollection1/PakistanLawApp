#!/usr/bin/env python3
"""
DigiLawyer Browser - Web scraping tool for legal databases.
"""

import os
import sys
import time
import json
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class DigiLawyerBrowser:
    """Browser automation for legal database scraping."""
    
    def __init__(self, headless=True, timeout=30):
        self.timeout = timeout
        self.driver = None
        self.headless = headless
        self.setup_driver()
        
    def setup_driver(self):
        """Initialize the Chrome driver."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Common options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Disable images for faster loading
        chrome_options.add_experimental_option(
            'prefs',
            {
                'profile.managed_default_content_settings.images': 2,
                'disk-cache-size': 4096
            }
        )
        
        # Try to find chromedriver
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            print("Make sure Chrome and chromedriver are installed.")
            sys.exit(1)
        
        self.driver.set_page_load_timeout(self.timeout)
        print("Browser initialized successfully")
    
    def navigate(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            bool: True if navigation successful
        """
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for page to load
            return True
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
    
    def find_element(self, selector: str, by=By.CSS_SELECTOR, timeout=None):
        """
        Find an element on the page.
        
        Args:
            selector: CSS selector or XPath
            by: Selector strategy
            timeout: Optional custom timeout
            
        Returns:
            WebElement or None
        """
        try:
            wait_time = timeout or self.timeout
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            return None
    
    def find_elements(self, selector: str, by=By.CSS_SELECTOR):
        """
        Find multiple elements on the page.
        
        Args:
            selector: CSS selector or XPath
            by: Selector strategy
            
        Returns:
            List of WebElements
        """
        try:
            return self.driver.find_elements(by, selector)
        except Exception as e:
            print(f"Failed to find elements: {e}")
            return []
    
    def click(self, selector: str, by=By.CSS_SELECTOR) -> bool:
        """
        Click an element.
        
        Args:
            selector: Element selector
            by: Selector strategy
            
        Returns:
            bool: True if click successful
        """
        try:
            element = self.find_element(selector, by)
            if element:
                element.click()
                time.sleep(1)
                return True
            return False
        except Exception as e:
            print(f"Click failed: {e}")
            return False
    
    def input_text(self, selector: str, text: str, by=By.CSS_SELECTOR) -> bool:
        """
        Input text into a field.
        
        Args:
            selector: Input field selector
            text: Text to input
            by: Selector strategy
            
        Returns:
            bool: True if input successful
        """
        try:
            element = self.find_element(selector, by)
            if element:
                element.clear()
                element.send_keys(text)
                return True
            return False
        except Exception as e:
            print(f"Input failed: {e}")
            return False
    
    def get_page_source(self) -> str:
        """Get the current page source."""
        return self.driver.page_source
    
    def get_current_url(self) -> str:
        """Get the current URL."""
        return self.driver.current_url
    
    def scroll_down(self, pixels=500):
        """Scroll down the page."""
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(0.5)
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
    
    def wait_for_element(self, selector: str, by=By.CSS_SELECTOR, timeout=None):
        """Wait for an element to appear."""
        try:
            wait_time = timeout or self.timeout
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException:
            return None
    
    def take_screenshot(self, filepath: str):
        """Take a screenshot."""
        self.driver.save_screenshot(filepath)
        print(f"Screenshot saved to {filepath}")
    
    def execute_script(self, script: str):
        """Execute JavaScript on the page."""
        return self.driver.execute_script(script)
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            print("Browser closed")


class DigiLawyerScraper:
    """Scraper for DigiLawyer legal database."""
    
    def __init__(self, browser: DigiLawyerBrowser):
        self.browser = browser
        self.base_url = "https://digilawyer.com"
        self.results = []
    
    def search_cases(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for cases on DigiLawyer.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of case dictionaries
        """
        print(f"Searching for: {query}")
        
        # Navigate to search page
        search_url = f"{self.base_url}/search"
        if not self.browser.navigate(search_url):
            return []
        
        # Input search query
        if not self.browser.input_text("#search-input", query):
            print("Failed to find search input")
            return []
        
        # Submit search
        if not self.browser.click("#search-submit"):
            print("Failed to submit search")
            return []
        
        # Wait for results
        time.sleep(3)
        
        # Extract results
        cases = []
        result_elements = self.browser.find_elements(".case-result")
        
        for element in result_elements[:max_results]:
            try:
                case = {
                    'title': element.find_element(By.CSS_SELECTOR, '.case-title').text,
                    'citation': element.find_element(By.CSS_SELECTOR, '.case-citation').text,
                    'court': element.find_element(By.CSS_SELECTOR, '.case-court').text,
                    'date': element.find_element(By.CSS_SELECTOR, '.case-date').text,
                    'summary': element.find_element(By.CSS_SELECTOR, '.case-summary').text,
                    'url': element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                }
                cases.append(case)
            except NoSuchElementException:
                continue
        
        print(f"Found {len(cases)} cases")
        return cases
    
    def get_case_details(self, case_url: str) -> Optional[Dict]:
        """
        Get detailed case information.
        
        Args:
            case_url: URL of the case
            
        Returns:
            Case dictionary or None
        """
        print(f"Fetching case details: {case_url}")
        
        if not self.browser.navigate(case_url):
            return None
        
        time.sleep(2)
        
        try:
            case = {
                'title': self.browser.find_element('h1.case-title').text,
                'citation': self.browser.find_element('.citation').text,
                'court': self.browser.find_element('.court-name').text,
                'date': self.browser.find_element('.decision-date').text,
                'judges': self.browser.find_element('.judges').text,
                'full_text': self.browser.find_element('.case-full-text').text,
                'headnotes': self.browser.find_element('.headnotes').text,
                'url': case_url
            }
            return case
        except Exception as e:
            print(f"Failed to extract case details: {e}")
            return None
    
    def scrape_category(self, category: str, max_pages: int = 5) -> List[Dict]:
        """
        Scrape cases from a category.
        
        Args:
            category: Category name
            max_pages: Maximum pages to scrape
            
        Returns:
            List of case dictionaries
        """
        print(f"Scraping category: {category}")
        
        category_url = f"{self.base_url}/category/{category}"
        if not self.browser.navigate(category_url):
            return []
        
        all_cases = []
        
        for page in range(1, max_pages + 1):
            print(f"Processing page {page}")
            
            # Extract cases from current page
            cases = self.extract_cases_from_page()
            all_cases.extend(cases)
            
            # Navigate to next page
            next_button = self.browser.find_element('.pagination-next')
            if not next_button or not next_button.is_enabled():
                break
            
            next_button.click()
            time.sleep(2)
        
        print(f"Total cases scraped: {len(all_cases)}")
        return all_cases
    
    def extract_cases_from_page(self) -> List[Dict]:
        """Extract cases from current page."""
        cases = []
        case_elements = self.browser.find_elements('.case-item')
        
        for element in case_elements:
            try:
                case = {
                    'title': element.find_element(By.CSS_SELECTOR, '.case-title').text,
                    'citation': element.find_element(By.CSS_SELECTOR, '.case-citation').text,
                    'court': element.find_element(By.CSS_SELECTOR, '.case-court').text,
                    'date': element.find_element(By.CSS_SELECTOR, '.case-date').text,
                    'summary': element.find_element(By.CSS_SELECTOR, '.case-summary').text,
                    'url': element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                }
                cases.append(case)
            except NoSuchElementException:
                continue
        
        return cases
    
    def save_results(self, filepath: str):
        """Save scraped results to file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {filepath}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='DigiLawyer Browser Scraper')
    parser.add_argument('--search', help='Search query')
    parser.add_argument('--category', help='Category to scrape')
    parser.add_argument('--url', help='Case URL to scrape')
    parser.add_argument('--output', default='digilawyer_results.json', help='Output file')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum results')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum pages')
    
    args = parser.parse_args()
    
    # Initialize browser
    browser = DigiLawyerBrowser(headless=args.headless)
    scraper = DigiLawyerScraper(browser)
    
    try:
        if args.search:
            results = scraper.search_cases(args.search, args.max_results)
            scraper.results = results
        elif args.category:
            results = scraper.scrape_category(args.category, args.max_pages)
            scraper.results = results
        elif args.url:
            result = scraper.get_case_details(args.url)
            scraper.results = [result] if result else []
        else:
            print("No action specified. Use --search, --category, or --url")
            return
        
        # Save results
        scraper.save_results(args.output)
        
    finally:
        browser.close()


if __name__ == "__main__":
    main()
