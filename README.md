# Ultra-Safe Multi-Symbol Crypto Bot

This bot trades **BTC, ETH, BNB, ADA, SOL** on Binance Futures using **ultra-safe risk management**.  

## Features

- Max loss per trade: **$0.005**  
- Daily loss limit: **6% of account**  
- ATR-based stop-loss, take-profit & trailing stop  
- Multi-symbol trading (safe coins only)  
- Telegram alerts for trades & errors  
- Heartbeat ping to prevent Render Free Tier from sleeping  
- Auto trade logging (`trade_log.csv`)

## Installation

1. Clone the repo:

```bash
git clone https://github.com/yourusername/crypto_bot.git
cd crypto_bot
