#!/bin/bash

# Deployment script for Telegram Crypto Bot
# This script handles deployment to various platforms

set -e

echo "🚀 Starting deployment process..."

# Check if environment variables are set
check_env_vars() {
    local required_vars=(
        "TELEGRAM_BOT_TOKEN"
        "DATABASE_URL"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        echo "❌ Missing environment variables: ${missing_vars[*]}"
        echo "Please set these variables before deployment"
        exit 1
    fi
    
    echo "✅ All required environment variables are set"
}

# Platform-specific deployment
deploy_to_platform() {
    if [[ -n "$REPLIT_DEPLOYMENT_ID" ]]; then
        echo "📦 Deploying to Replit..."
        python start_production.py
    elif [[ -n "$DYNO" ]]; then
        echo "📦 Deploying to Heroku..."
        python start_production.py
    elif [[ -n "$RAILWAY_ENVIRONMENT" ]]; then
        echo "📦 Deploying to Railway..."
        python start_production.py
    else
        echo "📦 Generic deployment..."
        python start_production.py
    fi
}

# Main deployment process
main() {
    echo "🔍 Checking environment..."
    check_env_vars
    
    echo "🏗️ Setting up production environment..."
    export PYTHONUNBUFFERED=1
    export PORT=${PORT:-5000}
    
    echo "🎯 Starting deployment..."
    deploy_to_platform
}

# Run deployment
main "$@"