from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import hashlib
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import utils.logger as Logger
import conf

class NitterScraper:
    """Scraper for Nitter (Twitter mirror) to extract tweets from specific accounts."""
    
    def __init__(self, html_dir=None, headless=False, timeout=10):
        if html_dir is None:
            html_dir = conf.SCRAPER_CONFIG.get('html_dir', 'html_output')
        self.html_dir = html_dir
        self.timeout = timeout
        os.makedirs(self.html_dir, exist_ok=True)
        self.logger = Logger.get_logger("NitterScraper")
        self.driver = self._init_driver(headless)
        self.wait = WebDriverWait(self.driver, self.timeout)

    def _init_driver(self, headless):
        """Initialize Chrome WebDriver with optimized options."""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        if headless:
            chrome_options.add_argument("--headless")
        else:
            chrome_options.add_argument("start-maximized")
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Chrome WebDriver initialized successfully")
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise




    def scrape_account(self, account, save_html=True):
        url = f"https://nitter.net/{account}"
        self.logger.info(f"Scraping {account}...")
        try:
            self.driver.get(url)
            
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.tweet-content"))
            )
            time.sleep(1)
            if save_html:
                html_path = os.path.join(self.html_dir, f"twitter_search_{account}.html")
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                self.logger.info(f"✓ HTML saved: {html_path}")
            return True
            
        except TimeoutException:
            self.logger.error(f"Timeout loading page for {account}")
            return False
        except Exception as e:
            self.logger.error(f"Error scraping {account}: {e}")
            return False


    def parse_account(self, account):
        html_path = os.path.join(self.html_dir, f"twitter_search_{account}.html")
        if not os.path.exists(html_path):
            self.logger.error(f"HTML file not found: {html_path}")
            return []
        try:
            with open(html_path, "r", encoding="utf-8") as file:
                html_content = file.read()
            soup = BeautifulSoup(html_content, "lxml")
            data = []
            tweets = soup.find_all("div", class_="tweet-body")
            for tweet in tweets:
                try:
                    username_elem = tweet.find("a", class_="username")
                    if not username_elem:
                        continue
                    pseudo = username_elem.text.strip()
                    date_elem = tweet.find("span", class_="tweet-date")
                    if not date_elem or not date_elem.find("a"):
                        continue
                    
                    date_link = date_elem.find("a")
                    if not date_link or not date_link.get("title"):
                        continue
                    full_date_str = date_link["title"].strip()
                    full_date_str = full_date_str.replace("·", "").replace("UTC", "").strip()
                    try:
                        dt = datetime.strptime(full_date_str, "%b %d, %Y %I:%M %p")
                    except ValueError:
                        try:
                            dt = datetime.strptime(full_date_str, "%b %d, %Y")
                        except ValueError:
                            self.logger.warning(f"Could not parse date: {full_date_str}")
                            continue
                    timestamp = int(dt.timestamp())
                    date_formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                    content_elem = tweet.find("div", class_="tweet-content")
                    if not content_elem:
                        continue
                    content = content_elem.text.strip()
                    content_cleaned = self._clean_tweet(content)
                    
                    data.append({
                        "pseudo": pseudo,
                        "account": account,
                        "content": content_cleaned,
                        "hash_content": hashlib.sha256(content_cleaned.encode()).hexdigest(),
                        "content_raw": content,
                        "timestamp": timestamp,
                        "date_str": date_formatted,  
                        "date_full": full_date_str  
                    })
                except Exception as e:
                    self.logger.warning(f"Error parsing tweet: {e}")
                    continue
            self.logger.info(f"{account}: {len(data)} tweets parsed")
            return data
        except Exception as e:
            self.logger.error(f"Error parsing {account}: {e}")
            return []


    def _clean_tweet(self, tweet):
        tweet = re.sub(r'·\s*\d+[mh]', '', tweet)
        tweet = re.sub(r'·\s*[A-Za-z]{3}\s\d{1,2}', '', tweet)
        tweet = re.sub(r'\s\d+(\.\d+)?[KkMm]?\b', '', tweet)
        tweet = ' '.join(tweet.split())
        return tweet.strip()
    

    def close(self):
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


