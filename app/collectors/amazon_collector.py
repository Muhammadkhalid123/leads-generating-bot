import asyncio
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from app.collectors.base import BaseCollector
from app.models.lead import LeadCreate
from app.config import settings

logger = logging.getLogger(__name__)

class AmazonCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.source_name = "amazon"
        self.driver = None
    
    def _init_driver(self):
        """Initialize headless Chrome."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Using webdriver_manager for easier setup
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
    
    def _detect_formatting_issues(self, look_inside_html: str) -> List[str]:
        """Analyze 'Look Inside' content for formatting problems."""
        issues = []
        soup = BeautifulSoup(look_inside_html, 'html.parser')
        
        # Check for common issues in the rendered view
        text_content = soup.get_text()
        
        # 1. Detect inconsistent spacing
        if re.search(r'\n{3,}', text_content):
            issues.append("inconsistent_paragraph_spacing")
        
        # 2. Detect missing TOC (check for "Table of Contents" but no links)
        toc_mentions = re.findall(r'(?i)table\s+of\s+contents', text_content)
        link_count = len(soup.find_all('a'))
        if toc_mentions and link_count < 3:
            issues.append("broken_or_unlinked_toc")
        
        # 3. Detect orphan control characters
        if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', text_content):
            issues.append("hidden_control_characters")
        
        # 4. Detect potential font inconsistencies (looking for mixed font-family styles)
        style_tags = soup.find_all(['span', 'p', 'div'], style=True)
        fonts_used = set()
        for tag in style_tags:
            style = tag.get('style', '')
            font_match = re.search(r'font-family:\s*([^;]+)', style)
            if font_match:
                fonts_used.add(font_match.group(1).strip())
        if len(fonts_used) > 2:
            issues.append("potential_font_inconsistency")
        
        # 5. Check for widows/orphans indicators (single words on lines)
        lines = text_content.split('\n')
        for line in lines:
            words = line.strip().split()
            if len(words) == 1 and len(words[0]) > 3 and line.strip().endswith('.'):
                issues.append("potential_widow_orphan")
                break
        
        return issues if issues else ["no_major_issues_detected"]
    
    def _extract_author_from_page(self, page_source: str) -> str:
        """Extract author name from Amazon product page."""
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Multiple selectors for author (Amazon changes these)
        author_selectors = [
            '.author a',
            '.contributorNameID',
            '#bylineInfo .author a',
            'span.author a',
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                return author_elem.text.strip()
        
        return "Unknown Author"
    
    async def collect(self) -> List[LeadCreate]:
        """Collect leads from Amazon KDP categories."""
        leads = []
        
        try:
            self._init_driver()
            
            for category in settings.AMAZON_CATEGORIES:
                # Navigate to Amazon bestsellers in category (new releases)
                url = f"https://www.amazon.com/s?i=stripbooks&rh=n%3A{category}&s=date-desc-rank"
                self.driver.get(url)
                
                await asyncio.sleep(2)  # Respect rate limits
                
                # Get book links
                book_links = self.driver.find_elements(By.CSS_SELECTOR, 'h2 a.a-link-normal')
                
                for i, link in enumerate(book_links[:10]):  # Limit to 10 per category
                    try:
                        book_url = link.get_attribute('href')
                        asin_match = re.search(r'/dp/(\w+)', book_url)
                        asin = asin_match.group(1) if asin_match else "UNKNOWN"
                        
                        # Open book page
                        self.driver.execute_script(f"window.open('{book_url}', '_blank');")
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        
                        await asyncio.sleep(1)
                        
                        # Extract book title
                        try:
                            title_elem = self.driver.find_element(By.ID, 'ebooksProductTitle')
                            book_title = title_elem.text.strip()
                        except:
                            book_title = "Unknown Title"
                        
                        # Extract author
                        author = self._extract_author_from_page(self.driver.page_source)
                        
                        # Try "Look Inside" feature
                        try:
                            look_inside_btn = self.driver.find_element(By.ID, 'ebooksImgBlkFront')
                            look_inside_btn.click()
                            await asyncio.sleep(2)
                            
                            # Get Look Inside content
                            look_inside_html = self.driver.page_source
                            formatting_issues = self._detect_formatting_issues(look_inside_html)
                        except:
                            formatting_issues = ["look_inside_not_available"]
                        
                        # Only capture if issues found (or specifically targeting all)
                        if formatting_issues and formatting_issues != ["no_major_issues_detected"]:
                            lead = LeadCreate(
                                source="amazon",
                                source_url=book_url,
                                source_id=asin,
                                author_name=author,
                                book_title=book_title,
                                book_asin=asin,
                                book_category=category,
                                formatting_issues=formatting_issues,
                                pain_point_summary=f"Formatting issues: {', '.join(formatting_issues)}",
                                relevance_score=70 + (len(formatting_issues) * 5),
                                discovered_at=datetime.now(),
                                raw_content=f"Book: {book_title}\nAuthor: {author}\nIssues: {formatting_issues}"
                            )
                            leads.append(lead)
                        
                        # Close tab and switch back
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        
                    except Exception as e:
                        logger.error(f"Error processing book #{i}: {e}")
                        # Ensure we switch back to main window
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                        continue
                        
        finally:
            if self.driver:
                self.driver.quit()
        
        self.log_collection(len(leads))
        return leads
