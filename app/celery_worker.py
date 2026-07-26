# app/celery_worker.py
import asyncio
import os
from celery import Celery
from app.config import settings
from app.collectors.reddit_collector import RedditCollector
from app.collectors.upwork_collector import UpworkCollector
from app.collectors.amazon_collector import AmazonCollector
from app.normalizer.lead_normalizer import LeadNormalizer
from app.main import process_lead

celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Initialize components
reddit_collector = RedditCollector()
upwork_collector = UpworkCollector()
amazon_collector = AmazonCollector()
normalizer = LeadNormalizer()

@celery_app.task(name="collect_reddit")
def collect_reddit_task():
    loop = asyncio.get_event_loop()
    raw_leads = loop.run_until_complete(reddit_collector.collect())
    normalized = normalizer.normalize(raw_leads)
    for lead in normalized:
        loop.run_until_complete(process_lead(lead))
    return f"Reddit: Processed {len(normalized)} leads"

@celery_app.task(name="collect_upwork")
def collect_upwork_task():
    loop = asyncio.get_event_loop()
    raw_leads = loop.run_until_complete(upwork_collector.collect())
    normalized = normalizer.normalize(raw_leads)
    for lead in normalized:
        loop.run_until_complete(process_lead(lead))
    return f"Upwork: Processed {len(normalized)} leads"

@celery_app.task(name="collect_amazon")
def collect_amazon_task():
    loop = asyncio.get_event_loop()
    raw_leads = loop.run_until_complete(amazon_collector.collect())
    normalized = normalizer.normalize(raw_leads)
    for lead in normalized:
        loop.run_until_complete(process_lead(lead))
    return f"Amazon: Processed {len(normalized)} leads"

# Celery Beat Schedule
celery_app.conf.beat_schedule = {
    "reddit-every-15-mins": {
        "task": "collect_reddit",
        "schedule": 900.0,
    },
    "upwork-every-30-mins": {
        "task": "collect_upwork",
        "schedule": 1800.0,
    },
    "amazon-daily": {
        "task": "collect_amazon",
        "schedule": 86400.0,
    },
}
