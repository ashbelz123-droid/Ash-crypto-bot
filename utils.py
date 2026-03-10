# utils.py

import threading, requests
from telegram import Bot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, HEARTBEAT_URL, PING_INTERVAL

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram(msg):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

def heartbeat():
    while True:
        try:
            requests.get(HEARTBEAT_URL)
            print("💓 Heartbeat ping sent")
        except Exception as e:
            print(f"⚠️ Heartbeat error: {e}")
        finally:
            import time
            time.sleep(PING_INTERVAL)

def start_heartbeat():
    threading.Thread(target=heartbeat, daemon=True).start()
