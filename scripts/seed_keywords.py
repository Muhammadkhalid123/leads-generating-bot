# scripts/seed_keywords.py
from app.database import SessionLocal
from app.models.lead import Keyword

KEYWORDS = [
    # HIRING INTENT - Reddit & Upwork
    {"keyword": "need formatter", "category": "hiring_intent", "source": "reddit", "weight": 10},
    {"keyword": "looking for formatter", "category": "hiring_intent", "source": "reddit", "weight": 10},
    {"keyword": "hire a formatter", "category": "hiring_intent", "source": "reddit", "weight": 10},
    {"keyword": "formatting help", "category": "hiring_intent", "source": "reddit", "weight": 8},
    {"keyword": "need book designer", "category": "hiring_intent", "source": "reddit", "weight": 9},
    {"keyword": "format my book", "category": "hiring_intent", "source": "reddit", "weight": 10},
    {"keyword": "someone format", "category": "hiring_intent", "source": "reddit", "weight": 9},
    {"keyword": "ebook services", "category": "hiring_intent", "source": "reddit", "weight": 7},
    {"keyword": "book formatting cost", "category": "hiring_intent", "source": "reddit", "weight": 8},
    {"keyword": "formatter recommendations", "category": "hiring_intent", "source": "reddit", "weight": 9},
    
    # PAIN POINTS
    {"keyword": "formatting nightmare", "category": "pain_point", "source": "reddit", "weight": 10},
    {"keyword": "broken toc", "category": "pain_point", "source": "reddit", "weight": 8},
    {"keyword": "table of contents broken", "category": "pain_point", "source": "reddit", "weight": 8},
    {"keyword": "margins messed up", "category": "pain_point", "source": "reddit", "weight": 8},
    {"keyword": "font inconsistent", "category": "pain_point", "source": "reddit", "weight": 7},
    {"keyword": "Kindle rejected", "category": "pain_point", "source": "reddit", "weight": 10},
    {"keyword": "KDP error", "category": "pain_point", "source": "reddit", "weight": 9},
    {"keyword": "epub won't validate", "category": "pain_point", "source": "reddit", "weight": 9},
    {"keyword": "formatting sucks", "category": "pain_point", "source": "reddit", "weight": 8},
    {"keyword": "hate formatting", "category": "pain_point", "source": "reddit", "weight": 9},
    
    # TOOL MENTIONS
    {"keyword": "Vellum alternative", "category": "tool_mention", "source": "reddit", "weight": 9},
    {"keyword": "Atticus formatting", "category": "tool_mention", "source": "reddit", "weight": 8},
    {"keyword": "Scrivener formatting", "category": "tool_mention", "source": "reddit", "weight": 8},
    {"keyword": "Calibre formatting", "category": "tool_mention", "source": "reddit", "weight": 7},
    {"keyword": "can't figure out KDP", "category": "tool_mention", "source": "reddit", "weight": 9},
    
    # UPWORK SPECIFIC
    {"keyword": "ebook formatting", "category": "hiring_intent", "source": "upwork", "weight": 10},
    {"keyword": "Kindle formatting", "category": "hiring_intent", "source": "upwork", "weight": 10},
    {"keyword": "book layout", "category": "hiring_intent", "source": "upwork", "weight": 9},
    {"keyword": "epub conversion", "category": "hiring_intent", "source": "upwork", "weight": 8},
    {"keyword": "mobi file", "category": "hiring_intent", "source": "upwork", "weight": 8},
    {"keyword": "paperback formatting", "category": "hiring_intent", "source": "upwork", "weight": 9},
    {"keyword": "book interior design", "category": "hiring_intent", "source": "upwork", "weight": 9},
]

def seed():
    db = SessionLocal()
    try:
        # Check if keywords already exist
        count = db.query(Keyword).count()
        if count > 0:
            print(f"Keywords already seeded ({count}). Skipping.")
            return

        for kw in KEYWORDS:
            keyword = Keyword(**kw)
            db.add(keyword)
        db.commit()
        print(f"Successfully seeded {len(KEYWORDS)} keywords.")
    except Exception as e:
        print(f"Error seeding keywords: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
