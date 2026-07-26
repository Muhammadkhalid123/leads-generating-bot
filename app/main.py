# app/main.py
import logging
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session

from app.collectors.reddit_collector import RedditCollector
from app.collectors.upwork_collector import UpworkCollector
from app.collectors.amazon_collector import AmazonCollector
from app.normalizer.lead_normalizer import LeadNormalizer
from app.enrichment.email_finder import EmailFinder
from app.outreach.ai_drafter import AIOutreachDrafter
from app.crm.google_sheets import GoogleSheetsCRM
from app.notifications.telegram_bot import TelegramNotifier
from app.database import engine, SessionLocal, get_db
from app.models.lead import Lead, LeadCreate, Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ebook Lead Engine")

# Initialize components
reddit_collector = RedditCollector()
upwork_collector = UpworkCollector()
amazon_collector = AmazonCollector()
normalizer = LeadNormalizer()
email_finder = EmailFinder()
ai_drafter = AIOutreachDrafter()
crm = GoogleSheetsCRM()
notifier = TelegramNotifier()

async def process_lead(lead_create: LeadCreate):
    """Pipeline: Enrich -> Draft -> Store -> Notify"""
    
    # Enrich with email if author name available
    if lead_create.author_name and lead_create.author_website:
        parts = lead_create.author_name.split()
        if len(parts) >= 2:
            domain = EmailFinder.extract_domain(lead_create.author_website)
            if domain:
                email = await EmailFinder.find_with_hunter(domain, parts[0], parts[-1])
                if email:
                    lead_create.author_email = email
    
    # Generate AI outreach draft
    if lead_create.relevance_score > 40:  # Only draft for decent leads
        draft = await ai_drafter.draft_outreach(lead_create)
        lead_create.outreach_draft = draft
    
    # Store in database
    db = SessionLocal()
    try:
        # Check for duplicates by source_id
        existing = db.query(Lead).filter(
            Lead.source == lead_create.source, 
            Lead.source_id == lead_create.source_id
        ).first()
        
        if existing:
            logger.info(f"Lead already exists: {lead_create.source_id}")
            return

        db_lead = Lead(**lead_create.dict(exclude={'fingerprint'}))
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        
        lead_dict = lead_create.dict()
        lead_dict['id'] = str(db_lead.id)
        
        # Sync to Google Sheets
        crm.sync_lead(lead_dict)
        
        # Notify if high value
        if lead_create.relevance_score >= 70:
            await notifier.notify_high_value_lead(lead_dict)
            
    except Exception as e:
        logger.error(f"Error saving lead: {e}")
        db.rollback()
    finally:
        db.close()

# Scheduled Collection Tasks

@app.on_event("startup")
@repeat_every(seconds=900)  # Every 15 minutes
async def collect_reddit():
    """Collect Reddit leads every 15 minutes."""
    logger.info("Starting Reddit collection...")
    raw_leads = await reddit_collector.collect()
    normalized = normalizer.normalize(raw_leads)
    for lead in normalized:
        await process_lead(lead)
    logger.info(f"Reddit: Processed {len(normalized)} leads")

@app.on_event("startup")
@repeat_every(seconds=1800)  # Every 30 minutes
async def collect_upwork():
    """Collect Upwork leads every 30 minutes."""
    logger.info("Starting Upwork collection...")
    raw_leads = await upwork_collector.collect()
    normalized = normalizer.normalize(raw_leads)
    for lead in normalized:
        await process_lead(lead)
    logger.info(f"Upwork: Processed {len(normalized)} leads")

@app.on_event("startup")
@repeat_every(seconds=86400)  # Daily
async def collect_amazon():
    """Collect Amazon leads once per day."""
    logger.info("Starting Amazon KDP collection...")
    raw_leads = await amazon_collector.collect()
    normalized = normalizer.normalize(raw_leads)
    for lead in normalized:
        await process_lead(lead)
    logger.info(f"Amazon: Processed {len(normalized)} leads")

# Health Check
@app.get("/health")
def health_check():
    return {"status": "running", "service": "ebook-lead-engine"}

# Manual Trigger Endpoints
@app.post("/trigger/reddit")
async def trigger_reddit(background_tasks: BackgroundTasks):
    background_tasks.add_task(collect_reddit)
    return {"message": "Reddit collection triggered in background"}

@app.post("/trigger/upwork")
async def trigger_upwork(background_tasks: BackgroundTasks):
    background_tasks.add_task(collect_upwork)
    return {"message": "Upwork collection triggered in background"}

@app.post("/trigger/amazon")
async def trigger_amazon(background_tasks: BackgroundTasks):
    background_tasks.add_task(collect_amazon)
    return {"message": "Amazon collection triggered in background"}
