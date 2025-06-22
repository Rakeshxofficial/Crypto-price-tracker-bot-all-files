# Render Deployment Guide

## Prerequisites
1. GitHub account with your bot code
2. Render account (free tier available)
3. All required API keys ready

## Step 1: Prepare Your Repository

1. Upload all project files to your GitHub repository: https://github.com/Rakeshxofficial/Marketbot
2. Ensure these files are included:
   - `render.yaml` (Render configuration)
   - `requirements.txt` (Python dependencies)
   - `start_production.py` (Production startup script)
   - All service files (.py files)

## Step 2: Create Render Services

### Option A: Using render.yaml (Recommended)
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Select your repository: `Rakeshxofficial/Marketbot`
5. Render will automatically detect `render.yaml` and create services

### Option B: Manual Setup
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect GitHub and select your repository
4. Configure the service:
   - **Name**: telegram-crypto-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `python start_production.py`
   - **Plan**: Starter (Free tier)

## Step 3: Configure Environment Variables

In your Render service settings, add these environment variables:

**Required Variables:**
```
TELEGRAM_BOT_TOKEN=7637510033:AAGan5C-cFg8MsZ3NOK4h0Id0My184BYZ5U
DATABASE_URL=postgresql://username:password@hostname:port/database
OPENAI_API_KEY=your_openai_key
COINGECKO_API_KEY=your_coingecko_key
RANGO_API_KEY=your_rango_key
```

**Optional Variables:**
```
COVALENT_API_KEY=your_covalent_key
TRON_API_KEY=your_tron_key
PYTHONUNBUFFERED=1
PORT=5000
```

## Step 4: Database Setup

### Option A: Render PostgreSQL (Recommended)
1. In Render Dashboard, click "New" → "PostgreSQL"
2. **Name**: postgres-db
3. **Plan**: Starter (Free tier)
4. Copy the database URL from the PostgreSQL service
5. Add it as `DATABASE_URL` in your web service environment variables

### Option B: External Database
Use any PostgreSQL provider (Neon, Supabase, etc.) and add the connection URL as `DATABASE_URL`

## Step 5: Deploy

1. Click "Create Web Service" or "Deploy Latest Commit"
2. Render will:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start your bot using `start_production.py`
   - Provide a public URL for health checks

## Step 6: Monitor Deployment

1. Check the deployment logs in Render Dashboard
2. Look for these success indicators:
   - "Bot is deployment-ready!"
   - "Application started"
   - "Bot commands menu set successfully"
   - "Price monitoring task started"

## Step 7: Test Your Bot

1. Message your Telegram bot
2. Try commands like `/start`, `/price bitcoin`
3. Monitor logs in Render Dashboard for any errors

## Troubleshooting

### Common Issues:

**1. Environment Variables Not Set**
- Verify all required API keys are configured
- Check for typos in variable names

**2. Database Connection Errors**
- Ensure DATABASE_URL is correctly formatted
- Verify PostgreSQL service is running

**3. Build Failures**
- Check `requirements.txt` for dependency conflicts
- Review build logs for specific error messages

**4. Bot Not Responding**
- Verify TELEGRAM_BOT_TOKEN is correct
- Check if webhook is disabled (handled automatically)

### Health Check
Your bot includes a health endpoint at `/` that Render uses to monitor service health.

## Render-Specific Optimizations

The bot includes production configurations that handle:
- Threading issues in containerized environments
- Automatic webhook cleanup
- Error recovery and retries
- Resource optimization for Render's infrastructure

## Cost Considerations

**Free Tier Limits:**
- Web Service: 750 hours/month
- PostgreSQL: 1GB storage, 1 month retention
- Automatic sleep after 15 minutes of inactivity

**Upgrade Options:**
- Starter Plan: $7/month for always-on service
- Professional Plan: $25/month for advanced features

## Environment Variables Reference

```bash
# Core Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:pass@host:port/db

# AI and Market Data
OPENAI_API_KEY=your_openai_key
COINGECKO_API_KEY=your_coingecko_key

# Cross-Chain Features
RANGO_API_KEY=your_rango_key
COVALENT_API_KEY=your_covalent_key
TRON_API_KEY=your_tron_key

# System Configuration
PYTHONUNBUFFERED=1
PORT=5000
```

Your bot will be accessible 24/7 once deployed to Render with all features fully operational.