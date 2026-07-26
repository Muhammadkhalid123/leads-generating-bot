from enum import Enum

class LeadSource(str, Enum):
    REDDIT = "reddit"
    UPWORK = "upwork"
    AMAZON = "amazon"
    BARK = "bark"

class LeadStatus(str, Enum):
    NEW = "new"
    ENRICHED = "enriched"
    CONTACTED = "contacted"
    REPLIED = "replied"
    CONVERTED = "converted"
    DEAD = "dead"

class KeywordCategory(str, Enum):
    HIRING_INTENT = "hiring_intent"
    PAIN_POINT = "pain_point"
    TOOL_MENTION = "tool_mention"
