# Telegram Crypto Bot Deployment Guide

## Required Environment Variables
Ensure these are set in your production environment:

```
TELEGRAM_BOT_TOKEN=7637510033:AAGan5C-cFg8MsZ3NOK4h0Id0My184BYZ5U
OPENAI_API_KEY=your_openai_key
COINGECKO_API_KEY=your_coingecko_key
RANGO_API_KEY=your_rango_key
DATABASE_URL=your_postgres_url
```

## Port Configuration
The bot runs on port 5000 by default. Ensure your deployment platform allows this.

## Production Considerations

### 1. Database Setup
- Ensure PostgreSQL is available
- Database tables are created automatically
- Connection pooling is configured

### 2. Threading Fix for Production
The bot uses alternative polling method to handle threading issues in containerized environments.

### 3. Memory Requirements
- Minimum 512MB RAM recommended
- Bot caches API responses for efficiency

### 4. Network Access
Ensure outbound connections are allowed for:
- Telegram API (api.telegram.org)
- CoinGecko API
- OpenAI API
- Rango Exchange API

## Deployment Checklist
- [ ] All environment variables configured
- [ ] Database accessible
- [ ] Port 5000 available
- [ ] Outbound network access enabled
- [ ] Sufficient memory allocated

## Troubleshooting
- Check logs for token authentication errors
- Verify database connectivity
- Ensure all API keys are valid
- Check memory and CPU limits