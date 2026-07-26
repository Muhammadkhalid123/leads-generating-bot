from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, Text, ARRAY, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from app.models.enums import LeadSource, LeadStatus

Base = declarative_base()

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    source = Column(String(20), nullable=False)
    weight = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(20), nullable=False)
    source_url = Column(Text)
    source_id = Column(String(255))
    
    # Author / Client Info
    author_name = Column(String(255))
    author_email = Column(String(255))
    author_website = Column(String(500))
    reddit_username = Column(String(100))
    
    # Book / Project Info
    book_title = Column(String(500))
    book_asin = Column(String(20))
    book_category = Column(String(100))
    
    # Pain Points Detected
    formatting_issues = Column(JSONB)
    pain_point_summary = Column(Text)
    matched_keywords = Column(ARRAY(String))
    
    # Metadata
    raw_content = Column(Text)
    relevance_score = Column(Float, default=0.0)
    outreach_draft = Column(Text)
    
    # Status Tracking
    status = Column(String(30), default='new')
    contacted_at = Column(DateTime)
    notes = Column(Text)
    
    # Timestamps
    discovered_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Pydantic models for API and Collectors
class LeadCreate(BaseModel):
    source: str
    source_url: Optional[str] = None
    source_id: Optional[str] = None
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    author_website: Optional[str] = None
    reddit_username: Optional[str] = None
    book_title: Optional[str] = None
    book_asin: Optional[str] = None
    book_category: Optional[str] = None
    formatting_issues: Optional[List[str]] = None
    pain_point_summary: Optional[str] = None
    matched_keywords: Optional[List[str]] = None
    raw_content: Optional[str] = None
    relevance_score: float = 0.0
    status: str = "new"
    discovered_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    fingerprint: Optional[str] = None
