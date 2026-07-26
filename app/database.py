from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
from typing import List, Dict

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_db_keywords(source: str = None) -> List[Dict]:
    """Helper to fetch active keywords for collectors."""
    from app.models.lead import Keyword
    db = SessionLocal()
    try:
        query = db.query(Keyword).filter(Keyword.is_active == True)
        if source:
            query = query.filter(Keyword.source == source)
        keywords = query.all()
        return [{"keyword": k.keyword, "weight": k.weight, "category": k.category} for k in keywords]
    finally:
        db.close()
