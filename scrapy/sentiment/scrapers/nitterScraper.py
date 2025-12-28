import tempfile
from scrapy.sentiment import service
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

import scrapy.utils.logger as Logger
import scrapy.config.settings as conf

class NitterScraper:
    """Scraper for Nitter (Twitter mirror) to extract tweets from specific accounts."""
    
    def __init__(self, html_dir=None, headless=False, timeout=10):
        """Initialize the Nitter scraper with Chrome WebDriver.
        
        Args:
            html_dir (str, optional): Directory to save scraped HTML files. Defaults to conf setting.
            headless (bool, optional): Run browser in headless mode. Defaults to False.
            timeout (int, optional): Timeout for WebDriver waits in seconds. Defaults to 10.
        """
        if html_dir is None:
            html_dir = conf.SCRAPER_CONFIG.get('html_dir', 'html_output')
        self.html_dir = html_dir
        self.nitter_base_url = conf.NITTER_INSTANCES
        self.max_retry_per_instance = conf.NITTER_MAX_RETRY_PER_INSTANCE
        self.retry_delays = conf.NITTER_RETRY_DELAYS
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
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=1920,1080")
        profile_dir = tempfile.mkdtemp(prefix="chrome_profile_")
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        if headless:
            chrome_options.add_argument("--headless=new")
        else:
            chrome_options.add_argument("start-maximized")
        try:
            #chrome_options.binary_location = "/usr/bin/google-chrome" # Uncomment and set path if needed
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Chrome WebDriver initialized successfully")
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise




    def scrape_account(self, account, save_html=True, max_retries=None):
        """Scrape tweets from a Twitter account using Nitter instances.
        
        Attempts to scrape from multiple Nitter instances with retry logic.
        Falls back to next instance if current one fails after max retries.
        Saves HTML to disk for later parsing.
        
        Args:
            account (str): Twitter account handle (without @)
            save_html (bool, optional): Whether to save HTML to disk. Defaults to True.
            max_retries (int, optional): Max retry attempts per instance. Defaults to config value.
            
        Returns:
            bool: True if scraping succeeded, False otherwise
        """
        if max_retries is None:
            max_retries = self.max_retry_per_instance
        self.logger.info(f"Scraping {account}...")
        
        for nitter_url in self.nitter_base_url:
            url = f"{nitter_url.rstrip('/')}/{account}"
            self.logger.info(f"Trying {nitter_url}...")
            for attempt in range(max_retries):
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
                        self.logger.info(f"HTML saved from {nitter_url}: {html_path}")
                    return True
                    
                except TimeoutException:
                    if attempt < max_retries - 1:
                        wait_time = self.retry_delays[attempt] if attempt < len(self.retry_delays) else self.retry_delays[-1]
                        self.logger.warning(f"Timeout on {nitter_url} for {account} (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        self.logger.warning(f"Timeout on {nitter_url} after {max_retries} attempts, switching to next instance...")
                        break 
                except Exception as e:
                    self.logger.warning(f"Error on {nitter_url}: {e}, switching to next instance...")
                    break 
        
        self.logger.error(f"Failed to scrape {account} from all Nitter instances")
        return False


    def parse_account(self, account):
        """Parse scraped HTML to extract tweet data.
        
        Reads saved HTML file and extracts tweet metadata including content,
        author, timestamp, and generates content hash for deduplication.
        
        Args:
            account (str): Twitter account handle that was scraped
            
        Returns:
            list: List of dictionaries containing tweet data:
                - pseudo: Username
                - account: Account handle
                - content: Cleaned tweet content
                - hash_content: SHA256 hash of content
                - content_raw: Original tweet content
                - timestamp: Unix timestamp
                - date_str: Formatted date string
                - date_full: Full date string from HTML
        """
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
        """Clean tweet content by removing metadata and normalizing whitespace.
        
        Removes timestamps, relative dates, engagement metrics (likes, retweets),
        and normalizes whitespace for consistent analysis.
        
        Args:
            tweet (str): Raw tweet content
            
        Returns:
            str: Cleaned tweet text
        """
        tweet = re.sub(r'·\s*\d+[mh]', '', tweet)
        tweet = re.sub(r'·\s*[A-Za-z]{3}\s\d{1,2}', '', tweet)
        tweet = re.sub(r'\s\d+(\.\d+)?[KkMm]?\b', '', tweet)
        tweet = ' '.join(tweet.split())
        return tweet.strip()
    

    def close(self):
        """Close WebDriver and clean up browser resources.
        
        Properly shuts down Chrome driver and associated processes.
        Safe to call multiple times.
        """
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver quit successfully")

            except Exception as e:
                self.logger.warning(f"Error during WebDriver quit: {e}")
            finally:
                try:
                    service = getattr(self.driver, "service", None)
                    if service and service.process:
                        service.stop()
                        self.logger.info("ChromeDriver service stopped")
                except Exception:
                    pass
                self.driver = None

    def __enter__(self):
        """Enter context manager (returns self)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and ensure cleanup."""
        self.close()


