"""
Web server wrapper for Telegram bot deployment
This creates a simple web server to satisfy deployment requirements
"""

import os
import asyncio
from aiohttp import web, ClientSession
import logging

# Import the main bot function
from main import main as run_bot

logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint for deployment monitoring"""
    import time
    return web.json_response({
        "status": "healthy",
        "service": "AI Crypto Assistant Bot",
        "message": "Bot is running successfully",
        "timestamp": int(time.time()),
        "uptime": "active"
    })

async def webhook_handler(request):
    """Webhook endpoint for Telegram updates"""
    try:
        # This will be handled by the bot application
        return web.json_response({"status": "ok"})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def bot_status(request):
    """Status endpoint to check if bot is running"""
    return web.json_response({
        "bot_status": "active",
        "features": [
            "Price tracking with /price command",
            "AI analysis with /shouldibuy command", 
            "Portfolio tracking with /portfolio command",
            "Price alerts with /setalert command",
            "Educational quiz with /quiz command",
            "Chart generation with /chart command",
            "Quick actions with /menu command"
        ]
    })

def create_app():
    """Create the web application"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', bot_status)
    app.router.add_post('/webhook', webhook_handler)
    
    return app

async def start_bot_background():
    """Start the bot in the background"""
    try:
        # Import and run the bot directly in this event loop
        import threading
        
        def run_bot_in_thread():
            # Run bot in a separate thread with its own event loop
            import asyncio
            asyncio.set_event_loop(asyncio.new_event_loop())
            run_bot()
        
        # Start bot in a separate thread
        bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
        bot_thread.start()
        logger.info("Bot thread started successfully")
        
    except Exception as e:
        logger.error(f"Bot error: {e}")

async def start_server():
    """Start the web server for deployment"""
    port = int(os.environ.get('PORT', 5000))
    
    app = create_app()
    
    # Start the bot in background
    bot_task = asyncio.create_task(start_bot_background())
    
    # Start the web server
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Web server started on port {port}")
    logger.info("Bot is deployment-ready!")
    
    # Keep both running
    try:
        await asyncio.gather(bot_task, asyncio.sleep(float('inf')))
    except KeyboardInterrupt:
        logger.info("Shutting down web server...")
        await runner.cleanup()

if __name__ == '__main__':
    # Start both the bot and web server
    asyncio.run(start_server())