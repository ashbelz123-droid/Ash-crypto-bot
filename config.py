# config.py

# ---------------- API KEYS ----------------
BINANCE_API_KEY = "YOUR_BINANCE_API_KEY"
BINANCE_API_SECRET = "YOUR_BINANCE_API_SECRET"

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# ---------------- TRADING SETTINGS ----------------
TRADING_SYMBOLS = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "SOL/USDT"]
TIMEFRAME = "5m"
LEVERAGE = 5

MAX_LOSS = 0.005          # Max $0.005 per trade
DAILY_LOSS_LIMIT_PERCENT = 6  # 6% daily loss stop
MIN_CONTRACT = 0.0001     # Minimum position size

# Heartbeat to prevent Render Free Tier sleep
HEARTBEAT_URL = "https://your-app.onrender.com/heartbeat"
PING_INTERVAL = 5*60  # every 5 minutes
