# app/enrichment/email_finder.py
import re
import requests
import logging
from typing import Optional, List
from app.config import settings

logger = logging.getLogger(__name__)

class EmailFinder:
    """Find email addresses using Hunter.io and permutation patterns."""
    
    COMMON_PATTERNS = [
        "{first}@{domain}",
        "{first}.{last}@{domain}",
        "{first}{last}@{domain}",
        "{f}{last}@{domain}",
        "{first}@gmail.com",
        "{first}{last}@gmail.com",
    ]
    
    @staticmethod
    def extract_domain(website: str) -> Optional[str]:
        """Extract domain from URL."""
        if not website:
            return None
        match = re.search(r'(?:https?://)?(?:www\.)?([^/\s]+)', website)
        return match.group(1) if match else None
    
    @staticmethod
    async def find_with_hunter(domain: str, first_name: str, last_name: str) -> Optional[str]:
        """Use Hunter.io API to find email."""
        if not settings.HUNTER_API_KEY:
            return None
        
        try:
            response = requests.get(
                "https://api.hunter.io/v2/email-finder",
                params={
                    "domain": domain,
                    "first_name": first_name,
                    "last_name": last_name,
                    "api_key": settings.HUNTER_API_KEY
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data", {}).get("email"):
                    return data["data"]["email"]
        except Exception as e:
            logger.error(f"Hunter.io error: {e}")
        
        return None
    
    @staticmethod
    def generate_permutations(first_name: str, last_name: str, domain: str) -> List[str]:
        """Generate email permutations based on name."""
        if not domain:
            return []
        
        first = first_name.lower().replace(" ", "")
        last = last_name.lower().replace(" ", "")
        f = first[0] if first else ""
        
        return [
            f"{first}@{domain}",
            f"{first}.{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{f}{last}@{domain}",
            f"{f}.{last}@{domain}",
            f"{first}_{last}@{domain}",
        ]
