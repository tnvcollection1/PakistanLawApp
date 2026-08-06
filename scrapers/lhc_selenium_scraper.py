"""
LHC Selenium Scraper - Scraper for LHC using Selenium
"""
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://lhc.gov.pk"

class LHCSeleniumScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape_judgments(self, page=1):
        url = f"{BASE_URL}/judgments?page={page}"
        self.driver.get(url)
        items = self.driver.find_elements(By.CSS_SELECTOR, '.judgment-item')
        judgments = []
        for item in items:
            judgments.append({
                'title': item.find_element(By.CSS_SELECTOR, '.title').text if item.find_elements(By.CSS_SELECTOR, '.title') else None,
                'date': item.find_element(By.CSS_SELECTOR, '.date').text if item.find_elements(By.CSS_SELECTOR, '.date') else None,
            })
        return judgments

    def close(self):
        self.driver.quit()

if __name__ == '__main__':
    scraper = LHCSeleniumScraper()
    judgments = scraper.scrape_judgments(1)
    print(json.dumps(judgments, indent=2))
    scraper.close()
