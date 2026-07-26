from abc import ABC, abstractmethod
from typing import List
from app.models.lead import LeadCreate
import logging

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """Abstract base for all lead collectors."""
    
    def __init__(self):
        self.source_name = "base"
    
    @abstractmethod
    async def collect(self) -> List[LeadCreate]:
        """Collect raw leads from source. Returns list of LeadCreate objects."""
        pass
    
    def log_collection(self, count: int):
        logger.info(f"[{self.source_name}] Collected {count} raw leads")
    
    def sanitize_text(self, text: str) -> str:
        """Basic text sanitization."""
        import re
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
