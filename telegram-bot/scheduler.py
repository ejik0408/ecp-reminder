from apscheduler.schedulers.background import BackgroundScheduler
from telegram_bot import send_daily_notification
from spreadsheet import get_expiring_soon, format_notification
from config import ADMIN_CHAT_ID
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def check_and_notify():
    try:
        expiring = get_expiring_soon([30, 14, 7, 3, 1])
        
        all_notifications = []
        for days in [30, 14, 7, 3, 1]:
            if expiring.get(days):
                all_notifications.append(format_notification(expiring[days], days))
        
        overdue = expiring.get(-1, [])
        if overdue:
            all_notifications.append(format_notification(overdue, -1))
        
        if all_notifications:
            message = "📋 Напоминание об ЭЦП\n" + "\n".join(all_notifications)
            from aiogram import Bot
            from config import TELEGRAM_BOT_TOKEN
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bot.send_message(ADMIN_CHAT_ID, message))
            logger.info("Notification sent successfully")
    except Exception as e:
        logger.error(f"Error in scheduler: {e}")

def start_scheduler():
    scheduler.add_job(check_and_notify, 'cron', hour=9, minute=0)
    scheduler.start()
    logger.info("Scheduler started - notifications at 9:00 AM")
