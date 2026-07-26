# app/normalizer/lead_normalizer.py
import re
import hashlib
from typing import List
from app.models.lead import LeadCreate

class LeadNormalizer:
    """Standardize and clean raw leads before storage."""
    
    @staticmethod
    def normalize(leads: List[LeadCreate]) -> List[LeadCreate]:
        normalized = []
        
        for lead in leads:
            # 1. Generate unique fingerprint for dedup
            fingerprint_str = f"{lead.source}:{lead.source_id}:{lead.author_name}"
            lead.fingerprint = hashlib.md5(fingerprint_str.encode()).hexdigest()
            
            # 2. Clean author name
            if lead.author_name:
                lead.author_name = re.sub(r'[\s]+', ' ', lead.author_name).strip()
            
            # 3. Extract potential website mentions from raw content
            if lead.raw_content:
                urls = re.findall(r'(https?://[^\s]+)', lead.raw_content)
                if urls and not lead.author_website:
                    lead.author_website = urls[0]
            
            # 4. Cap relevance score
            lead.relevance_score = min(lead.relevance_score, 100)
            
            # 5. Add source-specific tags
            if lead.source == "reddit":
                lead.notes = f"Reddit user: u/{lead.reddit_username}" + (f" | {lead.notes}" if lead.notes else "")
            
            normalized.append(lead)
        
        return normalized
