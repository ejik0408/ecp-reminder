import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SHEETS_URL = os.getenv("SHEETS_URL")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
