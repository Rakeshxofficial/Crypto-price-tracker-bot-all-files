#!/usr/bin/env python3
"""
Production startup script for Telegram Crypto Bot
Handles deployment-specific configurations and error recovery
"""

import os
import sys
import asyncio
import logging
from main import main

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Verify all required environment variables are present"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("All required environment variables present")
    return True

def setup_production_settings():
    """Configure production-specific settings"""
    # Set production port (Render uses PORT environment variable)
    os.environ.setdefault('PORT', '5000')
    
    # Render-specific optimizations
    os.environ.setdefault('RENDER_DEPLOYMENT', '1')
    
    # Configure for production deployment
    os.environ.setdefault('PYTHONUNBUFFERED', '1')
    
    # Database connection pooling
    os.environ.setdefault('DB_POOL_SIZE', '10')
    os.environ.setdefault('DB_MAX_OVERFLOW', '20')
    
    logger.info("Production settings configured")

async def health_check():
    """Basic health check for deployment platforms"""
    try:
        # Test database connectivity
        from database import get_db
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        logger.info("Health check passed: Database accessible")
        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

def main_with_recovery():
    """Main function with error recovery for production"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Starting bot (attempt {retry_count + 1}/{max_retries})")
            
            # Check environment
            if not check_environment():
                logger.error("Environment check failed")
                sys.exit(1)
            
            # Setup production settings
            setup_production_settings()
            
            # Run health check
            if not asyncio.run(health_check()):
                logger.warning("Health check failed, but continuing...")
            
            # Start the bot
            main()
            break
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            retry_count += 1
            logger.error(f"Bot crashed: {e}")
            
            if retry_count < max_retries:
                logger.info(f"Retrying in 5 seconds... ({retry_count}/{max_retries})")
                import time
                time.sleep(5)
            else:
                logger.error("Max retries exceeded. Exiting.")
                sys.exit(1)

if __name__ == "__main__":
    main_with_recovery()
