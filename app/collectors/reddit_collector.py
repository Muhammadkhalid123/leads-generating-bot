import praw
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from app.collectors.base import BaseCollector
from app.models.lead import LeadCreate
from app.config import settings
from app.database import get_db_keywords

logger = logging.getLogger(__name__)

class RedditCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.source_name = "reddit"
        # Only initialize if credentials are provided
        if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
            self.reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT
            )
        else:
            self.reddit = None
            logger.warning("Reddit API credentials missing. RedditCollector will not work.")
    
    async def collect(self) -> List[LeadCreate]:
        if not self.reddit:
            return []
            
        leads = []
        keywords = await get_db_keywords(source="reddit")
        
        for subreddit_name in settings.TARGET_SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get posts from last 6 hours
                time_filter = datetime.utcnow() - timedelta(hours=6)
                
                for submission in subreddit.new(limit=50):
                    if datetime.fromtimestamp(submission.created_utc) < time_filter:
                        continue
                    
                    # Check post title + body
                    full_text = f"{submission.title.lower()} {submission.selftext.lower()}"
                    
                    matched_keywords = []
                    relevance_score = 0
                    
                    for kw in keywords:
                        if kw["keyword"].lower() in full_text:
                            matched_keywords.append(kw["keyword"])
                            relevance_score += kw["weight"]
                    
                    if matched_keywords:
                        lead = LeadCreate(
                            source="reddit",
                            source_url=f"https://reddit.com{submission.permalink}",
                            source_id=submission.id,
                            reddit_username=str(submission.author),
                            pain_point_summary=submission.title,
                            matched_keywords=matched_keywords,
                            raw_content=submission.selftext[:5000],
                            relevance_score=min(relevance_score, 100),
                            discovered_at=datetime.fromtimestamp(submission.created_utc)
                        )
                        leads.append(lead)
                
                # Also scan comments (high intent)
                for comment in subreddit.comments(limit=100):
                    comment_time = datetime.fromtimestamp(comment.created_utc)
                    if comment_time < time_filter:
                        continue
                    
                    comment_text = comment.body.lower()
                    matched_keywords = []
                    relevance_score = 0
                    
                    for kw in keywords:
                        if kw["keyword"].lower() in comment_text:
                            matched_keywords.append(kw["keyword"])
                            relevance_score += kw["weight"]
                    
                    if matched_keywords and relevance_score > 15:  # Higher threshold for comments
                        lead = LeadCreate(
                            source="reddit",
                            source_url=f"https://reddit.com{comment.permalink}",
                            source_id=comment.id,
                            reddit_username=str(comment.author),
                            pain_point_summary=comment.body[:300],
                            matched_keywords=matched_keywords,
                            raw_content=comment.body,
                            relevance_score=min(relevance_score, 100),
                            discovered_at=comment_time
                        )
                        leads.append(lead)
                        
            except Exception as e:
                logger.error(f"Error scraping r/{subreddit_name}: {e}")
                continue
        
        self.log_collection(len(leads))
        return leads
