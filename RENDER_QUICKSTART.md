# Quick Render Deployment Guide

## 1. Upload to GitHub
Upload all project files to: https://github.com/Rakeshxofficial/Marketbot

**Essential files for Render:**
- `render.yaml` - Deployment configuration
- `render_requirements.txt` - Dependencies (rename to requirements.txt)
- `start_production.py` - Production startup
- All `.py` service files
- `RENDER_DEPLOYMENT.md` - Full deployment guide

## 2. Connect to Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect GitHub repository: `Rakeshxofficial/Marketbot`
4. Render will auto-detect `render.yaml` configuration

## 3. Set Environment Variables

In Render service settings, add:

```
TELEGRAM_BOT_TOKEN=7637510033:AAGan5C-cFg8MsZ3NOK4h0Id0My184BYZ5U
DATABASE_URL=postgresql://user:pass@host:port/db
OPENAI_API_KEY=your_openai_key
COINGECKO_API_KEY=your_coingecko_key
RANGO_API_KEY=your_rango_key
```

## 4. Database Options

**Option A: Render PostgreSQL (Free)**
- Create new PostgreSQL service in Render
- Copy database URL to your web service

**Option B: External Database**
- Use Neon, Supabase, or other PostgreSQL provider
- Add connection URL as DATABASE_URL

## 5. Deploy

Click "Create Web Service" - Render will:
- Install dependencies
- Start your bot automatically
- Provide health monitoring

## 6. Monitor

Check deployment logs for:
- "Bot is deployment-ready!"
- "Application started"
- "Bot commands menu set successfully"

Your Telegram bot will be live and operational on Render's infrastructure with all advanced features working.