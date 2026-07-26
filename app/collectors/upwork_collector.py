import feedparser
import asyncio
import re
import logging
from datetime import datetime
from typing import List
from app.collectors.base import BaseCollector
from app.models.lead import LeadCreate
from app.config import settings
from app.database import get_db_keywords

logger = logging.getLogger(__name__)

class UpworkCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.source_name = "upwork"
    
    def _extract_country(self, description: str) -> str:
        """Extract country from Upwork job description."""
        pattern = r'<b>Country</b>:\s*(\w{2,3})'
        match = re.search(pattern, description)
        return match.group(1) if match else "UNKNOWN"
    
    def _extract_budget(self, description: str) -> str:
        """Extract budget if available."""
        pattern = r'<b>Budget</b>:\s*\$(\d+)'
        match = re.search(pattern, description)
        return match.group(1) if match else "Not specified"
    
    def _is_quality_client(self, description: str) -> bool:
        """Check for payment verified and hire rate."""
        if "Payment not verified" in description:
            return False
        return True
    
    async def collect(self) -> List[LeadCreate]:
        leads = []
        keywords = await get_db_keywords(source="upwork")
        
        for feed_url in settings.UPWORK_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    title = entry.title.lower()
                    summary = entry.summary.lower() if hasattr(entry, 'summary') else ""
                    full_text = f"{title} {summary}"
                    
                    # Extract country
                    country = self._extract_country(entry.summary)
                    
                    # Filter by target countries
                    if country not in settings.TARGET_COUNTRIES:
                        continue
                    
                    # Quality check
                    if not self._is_quality_client(entry.summary):
                        continue
                    
                    # Keyword matching
                    matched_keywords = []
                    relevance_score = 0
                    
                    for kw in keywords:
                        if kw["keyword"].lower() in full_text:
                            matched_keywords.append(kw["keyword"])
                            relevance_score += kw["weight"]
                    
                    if matched_keywords:
                        # Parse published date
                        published = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                        
                        budget = self._extract_budget(entry.summary)
                        
                        lead = LeadCreate(
                            source="upwork",
                            source_url=entry.link,
                            source_id=entry.id,
                            pain_point_summary=entry.title,
                            matched_keywords=matched_keywords,
                            raw_content=f"Title: {entry.title}\nSummary: {summary}\nBudget: ${budget}",
                            relevance_score=min(relevance_score, 100),
                            discovered_at=published,
                            notes=f"Budget: ${budget} | Country: {country}"
                        )
                        leads.append(lead)
                        
            except Exception as e:
                logger.error(f"Error parsing feed {feed_url}: {e}")
                continue
        
        self.log_collection(len(leads))
        return leads
