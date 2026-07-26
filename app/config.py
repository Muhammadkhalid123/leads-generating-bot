# app/config.py
import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://leads:leads_pass@localhost:5432/leads_db")
    
    # Reddit API
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: str = "ebook-lead-engine:v1.0"
    
    # Upwork
    UPWORK_RSS_FEEDS: List[str] = field(default_factory=lambda: [
        "https://www.upwork.com/ab/feed/jobs/rss?q=ebook+formatting",
        "https://www.upwork.com/ab/feed/jobs/rss?q=kindle+formatting",
        "https://www.upwork.com/ab/feed/jobs/rss?q=book+layout+design",
        "https://www.upwork.com/ab/feed/jobs/rss?q=kdp+formatting",
        "https://www.upwork.com/ab/feed/jobs/rss?q=epub+conversion",
    ])
    
    # Amazon Scraper
    AMAZON_CATEGORIES: List[str] = field(default_factory=lambda: [
        "books/self-help",
        "books/business",
        "books/romance",
        "books/fantasy",
        "books/science-fiction",
        "books/non-fiction",
    ])
    
    # Hunter.io
    HUNTER_API_KEY: str = os.getenv("HUNTER_API_KEY")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o-mini"  # Use mini for cost efficiency
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")
    
    # Google Sheets
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID")
    GOOGLE_CREDS_PATH: str = "google_creds.json"
    
    # Target Countries
    TARGET_COUNTRIES: List[str] = field(default_factory=lambda: [
        "US", "GB", "IE", "NZ", "AU", "NL", "CA"
    ])
    
    # Subreddit targets
    TARGET_SUBREDDITS: List[str] = field(default_factory=lambda: [
        "selfpublish",
        "selfpublishing",
        "ebooks",
        "writing",
        "eroticauthors",
        "KDP",
        "bookdesign",
        "hireaneditor",
        "authors",
        "BookCovers", 
        "bookformatting",
    ])

settings = Settings()
