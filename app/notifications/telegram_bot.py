# app/notifications/telegram_bot.py
import aiohttp
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def notify_high_value_lead(self, lead_data: dict):
        """Send alert for leads with relevance_score > 70."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram config missing. Skipping notification.")
            return
            
        message = f"""
🔥 <b>HIGH-VALUE LEAD DETECTED</b>
━━━━━━━━━━━━━━━━━━━━━━
📚 <b>Source:</b> {lead_data.get('source', 'Unknown')}
⭐ <b>Score:</b> {lead_data.get('relevance_score', 'N/A')}/100

📝 <b>Summary:</b> {lead_data.get('pain_point_summary', 'N/A')[:200]}

👤 <b>Author:</b> {lead_data.get('author_name', 'Unknown')}
📖 <b>Book:</b> {lead_data.get('book_title', 'N/A')}

🔗 <b>URL:</b> {lead_data.get('source_url', 'N/A')}

💡 <b>Action:</b> Draft outreach immediately
        """
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": False
                    }
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        logger.error(f"Telegram API error: {text}")
            except Exception as e:
                logger.error(f"Telegram notification failed: {e}")
    
    async def send_daily_summary(self, stats: dict):
        """Send daily collection statistics."""
        if not self.bot_token or not self.chat_id:
            return

        message = f"""
📊 <b>DAILY LEAD SUMMARY</b>
━━━━━━━━━━━━━━━━━━━━━━
🕐 <b>Time:</b> {stats.get('date', 'Today')}

📥 <b>Total Collected:</b> {stats.get('total', 0)}
├─ Reddit: {stats.get('reddit', 0)}
├─ Upwork: {stats.get('upwork', 0)}
└─ Amazon: {stats.get('amazon', 0)}

⭐ <b>High-Value (>70):</b> {stats.get('high_value', 0)}
📧 <b>Emails Found:</b> {stats.get('enriched', 0)}
        """
        
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "HTML"
                    }
                )
            except Exception as e:
                logger.error(f"Telegram summary failed: {e}")
