# app/crm/google_sheets.py
import gspread
import logging
import os
from oauth2client.service_account import ServiceAccountCredentials
from app.config import settings

logger = logging.getLogger(__name__)

class GoogleSheetsCRM:
    def __init__(self):
        self.client = None
        self.sheet = None
        
        if os.path.exists(settings.GOOGLE_CREDS_PATH) and settings.GOOGLE_SHEET_ID:
            try:
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name(settings.GOOGLE_CREDS_PATH, scope)
                self.client = gspread.authorize(creds)
                self.sheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1
            except Exception as e:
                logger.error(f"Failed to initialize Google Sheets: {e}")
        else:
            logger.warning("Google Sheets credentials or ID missing. Skipping CRM sync.")
    
    HEADERS = [
        "ID", "Discovered At", "Source", "Author Name", "Author Email",
        "Book Title", "Pain Points", "Relevance Score", "Status",
        "Outreach Draft", "Contacted At", "Notes", "Source URL"
    ]
    
    def sync_lead(self, lead: dict):
        """Append a new lead to the Google Sheet."""
        if not self.sheet:
            return
            
        try:
            row = [
                str(lead.get('id', '')),
                str(lead.get('discovered_at', '')),
                lead.get('source', ''),
                lead.get('author_name', ''),
                lead.get('author_email', ''),
                lead.get('book_title', ''),
                lead.get('pain_point_summary', ''),
                lead.get('relevance_score', ''),
                lead.get('status', 'new'),
                lead.get('outreach_draft', ''),
                str(lead.get('contacted_at', '')),
                lead.get('notes', ''),
                lead.get('source_url', '')
            ]
            self.sheet.append_row(row)
            logger.info(f"Synced lead to sheets: {lead.get('id')}")
        except Exception as e:
            logger.error(f"Google Sheets sync error: {e}")
