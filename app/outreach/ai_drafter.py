# app/outreach/ai_drafter.py
from openai import AsyncOpenAI
import logging
from app.config import settings
from app.models.lead import LeadCreate

logger = logging.getLogger(__name__)

class AIOutreachDrafter:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OpenAI API key missing. AIOutreachDrafter will not work.")
    
    def _select_template(self, source: str, pain_points: list) -> str:
        """Select appropriate template based on lead characteristics."""
        
        if source == "amazon":
            return """You are an outreach specialist for ebook formatting services. 
            Draft a friendly, non-pushy email to an author whose book on Amazon has formatting issues.
            
            Author: {author_name}
            Book: {book_title}
            Issues Detected: {formatting_issues}
            
            Rules:
            - Be casual and helpful, never critical
            - Mention you noticed the book and "thought the content was great"
            - Subtly point out the formatting issues as something that "might affect reader experience"
            - Offer a free 15-minute audit
            - Keep under 150 words
            - Include a Calendly link placeholder [CALENDLY_LINK]
            - Sign as "Ebook Production Specialist"
            """
        
        elif source == "reddit":
            return """You are drafting a Reddit DM or reply. The person posted about formatting struggles.
            
            Post: {pain_point_summary}
            Username: u/{reddit_username}
            
            Rules:
            - Be super casual, like a fellow Redditor
            - Share a quick tip related to their problem first
            - Then mention you do this professionally
            - No formal signature, just first name
            - Keep under 100 words
            - Don't be salesy
            """
        
        else:  # upwork, bark, etc.
            return """You are drafting a proposal response for an ebook formatting job.
            
            Job: {pain_point_summary}
            Details: {raw_content}
            
            Rules:
            - Professional but warm
            - Address their specific requirements
            - Mention quick turnaround and KDP compliance
            - Include portfolio mention
            - Keep under 200 words
            - Add call to action for call
            """
    
    async def draft_outreach(self, lead: LeadCreate) -> str:
        """Generate personalized outreach message."""
        if not self.client:
            return "Draft generation skipped (API key missing)."
            
        try:
            template = self._select_template(lead.source, lead.formatting_issues or [])
            
            # Format template with lead data
            prompt = template.format(
                author_name=lead.author_name or "Author",
                book_title=lead.book_title or "your book",
                formatting_issues=", ".join(lead.formatting_issues) if lead.formatting_issues else "general formatting",
                pain_point_summary=lead.pain_point_summary or "",
                raw_content=lead.raw_content or "",
                reddit_username=lead.reddit_username or "there",
            )
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Generate the outreach message now."}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            draft = response.choices[0].message.content.strip()
            return draft
            
        except Exception as e:
            logger.error(f"OpenAI drafting error: {e}")
            return "Draft generation failed. Please compose manually."
