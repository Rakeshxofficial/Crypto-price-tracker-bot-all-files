#!/bin/bash

# Render.com deployment setup script
# This script prepares the project for Render deployment

echo "🚀 Setting up project for Render deployment..."

# Copy requirements for Render
if [ -f "render_requirements.txt" ]; then
    cp render_requirements.txt requirements.txt
    echo "✅ Requirements file prepared for Render"
fi

# Set executable permissions
chmod +x start_production.py
echo "✅ Production script permissions set"

# Create Render-specific environment check
cat > render_health_check.py << 'EOF'
#!/usr/bin/env python3
"""
Health check endpoint for Render deployment
"""
import os
import sys
from aiohttp import web

async def health_check(request):
    """Health check endpoint for Render"""
    return web.json_response({
        "status": "healthy",
        "service": "telegram-crypto-bot",
        "environment": os.getenv("RENDER_DEPLOYMENT", "unknown")
    })

if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    port = int(os.getenv('PORT', 5000))
    web.run_app(app, host='0.0.0.0', port=port)
EOF

echo "✅ Health check endpoint created"

# Update render.yaml if needed
if [ -f "render.yaml" ]; then
    echo "✅ Render configuration file exists"
else
    echo "❌ render.yaml not found - please ensure it's created"
fi

echo "🎯 Render deployment setup complete!"
echo ""
echo "Next steps:"
echo "1. Push all files to GitHub repository"
echo "2. Connect GitHub to Render"
echo "3. Set environment variables in Render dashboard"
echo "4. Deploy the service"