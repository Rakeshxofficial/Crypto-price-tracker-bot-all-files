#!/usr/bin/env python3
"""
AI-Powered Telegram Crypto Assistant Bot
Features: Live prices, AI trading advice, alerts, portfolio tracking, trending analysis
"""

import os
import logging
import re
import asyncio
from typing import Dict
from datetime import datetime
from asyncio import create_task
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, SUPPORTED_CURRENCIES, DEFAULT_CURRENCIES, CURRENCY_SYMBOLS
from price_service import PriceService
from coin_mapper import CoinMapper
from ai_service import AIMarketAnalyst
from market_service import MarketService
from alert_service import AlertService
from portfolio_service import PortfolioService
from wallet_service import WalletService
from chart_service import ChartService
from quiz_service import CryptoQuizService
from recommendation_engine import PersonalizedRecommendationEngine
from token_scanner import TokenScanner
from token_risk_analyzer import TokenRiskAnalyzer
from currency_converter import CurrencyConverter
from user_service import UserService
from multi_wallet_service import MultiWalletService
from live_notification_service import LiveNotificationService
from rango_swap_service import RangoSwapService
from database import init_database

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize services
price_service = PriceService()
coin_mapper = CoinMapper()
ai_analyst = AIMarketAnalyst()
market_service = MarketService()
alert_service = AlertService()
portfolio_service = PortfolioService()
wallet_service = WalletService()
chart_service = ChartService()
quiz_service = CryptoQuizService()
recommendation_engine = PersonalizedRecommendationEngine()
token_scanner = TokenScanner()
risk_analyzer = TokenRiskAnalyzer()
currency_converter = CurrencyConverter()
user_service = UserService()
multi_wallet_service = MultiWalletService()
live_notification_service = LiveNotificationService()
rango_swap_service = RangoSwapService()

async def track_user_safely(user):
    """Track user interaction without blocking main bot responses"""
    try:
        await user_service.track_user(
            str(user.id), 
            user.username or "Unknown", 
            user.first_name or "Unknown", 
            user.last_name or ""
        )
    except Exception as e:
        logger.warning(f"Background user tracking failed: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    # First respond immediately to user, then track asynchronously
    user = update.effective_user
    
    # Track user interaction in background (completely non-blocking)
    if user:
        asyncio.create_task(track_user_safely(user))
    
    welcome_message = """
🤖 Welcome to AI Crypto Assistant!

Your intelligent crypto companion with AI-powered analysis and advanced features.

🚀 AI Features:
• /shouldibuy [COIN] - Get AI trading advice
• /trending - Top trending cryptocurrencies
• /daily - AI market summary

📊 Price & Data:
• /price [COIN] - Live cryptocurrency prices
• /allcoins - View all supported coins

🔔 Alerts & Portfolio:
• /setalert [COIN] [PRICE] - Set price alerts
• /alerts - View your active alerts
• /portfolio [WALLET] - Check wallet holdings
• /setwallet [WALLET] - Save default wallet

⚡ Quick Actions:
• /menu - Open quick actions menu

🎯 Personalized AI:
• /recommend - Get personalized investment recommendations
• /insights - Market insights based on your profile
• /riskprofile - Analyze your risk tolerance

💡 Get started: /shouldibuy bitcoin
💰 Supported: 220+ cryptocurrencies
"""
    
    # Create inline keyboard with community buttons
    keyboard = [
        [
            InlineKeyboardButton("📢 Join Channel", url="https://t.me/MarketPricetrack"),
            InlineKeyboardButton("👥 Join Community", url="https://t.me/marketpricetrackofficial"),
        ],
        [
            InlineKeyboardButton("🌐 Visit Website", url="https://marketpricetrack.com/"),
            InlineKeyboardButton("🔧 Bot Menu", callback_data="start_menu"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    help_message = """
🔥 **AI-Powered Crypto Assistant - Complete Command Guide**

**📊 Price & Market Data:**
• `/price [COIN]` - Live cryptocurrency prices
• `/setcurrency [CURRENCIES]` - Set preferred currencies (up to 5)
• `/convert [AMOUNT] [FROM] [TO]` - Currency converter with live rates
• `/chart [COIN] [DAYS]` - Price history charts (1, 7, 30, 90, 365 days)
• `/trending` - Top trending cryptocurrencies
• `/allcoins` - View all supported cryptocurrencies

**🤖 AI-Powered Analysis:**
• `/shouldibuy [COIN]` - AI trading advice & market analysis
• `/daily` - AI-generated daily market summary

**🎯 Personalized AI Recommendations:**
• `/recommend` - Get personalized investment recommendations
• `/insights` - Market insights based on your profile
• `/riskprofile` - Analyze your risk tolerance

**🔔 Price Alerts:**
• `/setalert [COIN] [PRICE] [above/below]` - Set price alerts
• `/alerts` - View your active alerts
• `/deletealert [ALERT_ID]` - Delete specific alert

**💼 Portfolio & Wallet Tracking:**
• `/portfolio [WALLET_ADDRESS] [CHAIN]` - Check wallet holdings
• `/setwallet [WALLET_ADDRESS] [CHAIN]` - Save default wallet

**⚡ Quick Actions:**
• `/menu` - Interactive Quick Actions menu

**🔍 Token Analysis:**
• `/scan [CHAIN] [TOKEN_ADDRESS]` - Multi-chain token analysis with AI risk assessment

**🎮 Educational Features:**
• `/quiz [difficulty]` - Start crypto/blockchain quiz (beginner/intermediate/advanced)
• `/quizstats` - View your quiz statistics

**ℹ️ Information:**
• `/start` - Welcome message
• `/help` - This comprehensive guide

**📋 Examples:**
• `/price BTC` - Bitcoin price
• `/setcurrency usd eur gbp jpy` - Set 4 preferred currencies
• `/convert 100 usd eur` - Convert $100 to EUR
• `/chart ETH 30` - Ethereum 30-day chart
• `/shouldibuy SOL` - AI analysis for Solana
• `/setalert BTC 50000 above` - Alert when Bitcoin hits $50k
• `/portfolio 0x123...abc eth` - Check Ethereum wallet
• `/recommend` - Get personalized investment advice
• `/riskprofile` - Analyze your investment style

**💡 Supported:**
• 200+ cryptocurrencies (BTC, ETH, SOL, ADA, etc.)
• Multiple blockchains (Ethereum, BSC, Polygon)
• Real-time notifications and monitoring

Use coin symbols (BTC) or full names (bitcoin) - both work!
"""
    
    # Create inline keyboard with community buttons
    keyboard = [
        [
            InlineKeyboardButton("📢 Join Channel", url="https://t.me/MarketPricetrack"),
            InlineKeyboardButton("👥 Join Community", url="https://t.me/marketpricetrackofficial"),
        ],
        [
            InlineKeyboardButton("🌐 Visit Website", url="https://marketpricetrack.com/"),
            InlineKeyboardButton("🔧 Bot Menu", callback_data="start_menu"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(help_message, reply_markup=reply_markup)

async def allcoins_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display all supported cryptocurrencies."""
    logger.info("Allcoins command requested")
    
    # Get all supported coins from the coin mapper
    coin_mapper = CoinMapper()
    supported_coins = coin_mapper.get_supported_coins()
    
    # Sort the coins alphabetically
    supported_coins.sort()
    
    # Create the message with coins grouped for better readability
    message_parts = ["🪙 All Supported Cryptocurrencies:\n"]
    
    # Group coins in chunks of 15 for better formatting
    for i in range(0, len(supported_coins), 15):
        chunk = supported_coins[i:i+15]
        line = " • ".join(chunk)
        message_parts.append(f"• {line}")
    
    # Add footer information
    message_parts.append(f"\n📊 Total supported: {len(supported_coins)} cryptocurrencies")
    message_parts.append("\n💡 Usage: /price <coin_name>")
    message_parts.append("Example: /price btc")
    
    full_message = "\n".join(message_parts)
    
    # Telegram has a message length limit, so we might need to split long messages
    if len(full_message) > 4096:
        # Split into multiple messages if too long
        current_message = "🪙 All Supported Cryptocurrencies:\n\n"
        
        for i in range(0, len(supported_coins), 20):
            chunk = supported_coins[i:i+20]
            chunk_text = " • ".join(chunk)
            
            if len(current_message + chunk_text) > 3800:  # Leave room for footer
                current_message += f"\n📊 Showing {i} cryptocurrencies..."
                await update.message.reply_text(current_message)
                current_message = f"🪙 Continued - Part {i//20 + 1}:\n\n"
            
            current_message += f"• {chunk_text}\n"
        
        # Send the final part
        current_message += f"\n📊 Total supported: {len(supported_coins)} cryptocurrencies"
        current_message += "\n💡 Usage: /price <coin_name>"
        await update.message.reply_text(current_message)
    else:
        await update.message.reply_text(full_message)

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /price command to fetch cryptocurrency prices."""
    try:
        # Check if coin argument is provided
        if not context.args:
            await update.message.reply_text(
                "❌ Please specify a cryptocurrency!\n\n"
                "Usage: /price [COIN]\n"
                "Example: /price BTC\n\n"
                "Type /help for more information."
            )
            return

        coin_input = context.args[0].lower()
        logger.info(f"Price request for: {coin_input}")

        # Map coin input to CoinGecko ID
        coin_id = coin_mapper.get_coin_id(coin_input)
        if not coin_id:
            await update.message.reply_text(
                f"❌ Cryptocurrency '{coin_input}' not found!\n\n"
                "Please check the spelling or try these popular coins:\n"
                "• BTC, ETH, SOL, ADA, DOT, MATIC\n"
                "• bitcoin, ethereum, solana, cardano\n\n"
                "Type /help for more examples."
            )
            return

        # Get user's preferred currencies
        user_id = str(update.effective_user.id)
        user_currencies = DEFAULT_CURRENCIES  # Default fallback
        
        if (hasattr(context, 'user_data') and context.user_data and 
            'user_currencies' in context.user_data and 
            user_id in context.user_data['user_currencies']):
            user_currencies = context.user_data['user_currencies'][user_id]
        
        # Fetch price data with user's preferred currencies
        price_data = await price_service.get_price(coin_id, user_currencies)
        if not price_data:
            await update.message.reply_text(
                f"❌ Unable to fetch price data for '{coin_input}' right now.\n\n"
                "This may be due to:\n"
                "• High API traffic (please wait 30 seconds and try again)\n"
                "• Invalid coin name\n\n"
                "Type /allcoins to see supported cryptocurrencies."
            )
            return

        # Format and send response
        response_message = format_price_message(coin_input, coin_id, price_data)
        await update.message.reply_text(response_message)

    except Exception as e:
        logger.error(f"Error in price_command: {e}")
        await update.message.reply_text(
            "❌ An unexpected error occurred.\n"
            "Please try again later."
        )

def format_price_message(coin_input: str, coin_id: str, price_data: dict) -> str:
    """Format the price data into a user-friendly message with multi-currency support."""
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime("%H:%M:%S UTC")
        
        # Get coin name (capitalize first letter of each word)
        coin_name = coin_id.replace('-', ' ').title()
        
        # Currency flag mapping
        currency_flags = {
            'usd': '🇺🇸', 'eur': '🇪🇺', 'gbp': '🇬🇧', 'jpy': '🇯🇵',
            'cad': '🇨🇦', 'aud': '🇦🇺', 'chf': '🇨🇭', 'cny': '🇨🇳',
            'inr': '🇮🇳', 'krw': '🇰🇷', 'sgd': '🇸🇬', 'hkd': '🇭🇰',
            'nzd': '🇳🇿', 'sek': '🇸🇪', 'nok': '🇳🇴', 'dkk': '🇩🇰',
            'pln': '🇵🇱', 'rub': '🇷🇺', 'brl': '🇧🇷', 'mxn': '🇲🇽',
            'zar': '🇿🇦', 'try': '🇹🇷', 'aed': '🇦🇪', 'sar': '🇸🇦'
        }
        
        # Build message
        message = f"💰 Live Price of {coin_name.upper()}:\n\n"
        
        # Add prices for each currency
        for currency in price_data:
            if currency != 'last_updated_at':
                price = price_data[currency]
                currency_upper = currency.upper()
                flag = currency_flags.get(currency, '🌍')
                symbol = CURRENCY_SYMBOLS.get(currency, currency_upper)
                
                # Format price based on currency (some currencies don't use decimals)
                if currency in ['jpy', 'krw']:
                    if price >= 1:
                        formatted_price = f"{symbol}{price:,.0f}"
                    else:
                        formatted_price = f"{symbol}{price:.2f}"
                else:
                    if price >= 1:
                        formatted_price = f"{symbol}{price:,.2f}"
                    else:
                        formatted_price = f"{symbol}{price:.6f}"
                
                message += f"{flag} {formatted_price} {currency_upper}\n"
        
        message += f"\n⏰ Updated: {timestamp}"
        message += "\n📊 Data by CoinGecko"
        
        return message
        
    except Exception as e:
        logger.error(f"Error formatting price message: {e}")
        return "❌ Error formatting price data."

async def shouldibuy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /shouldibuy command for AI trading advice."""
    try:
        if not context.args:
            await update.message.reply_text(
                "🤖 Get AI trading advice!\n\n"
                "Usage: /shouldibuy [COIN]\n"
                "Example: /shouldibuy bitcoin\n"
                "Example: /shouldibuy ETH"
            )
            return

        coin_input = context.args[0].lower()
        user_id = str(update.effective_user.id)
        
        # Map coin input to CoinGecko ID
        coin_id = coin_mapper.get_coin_id(coin_input)
        if not coin_id:
            await update.message.reply_text(
                f"❌ Cryptocurrency '{coin_input}' not found!\n\n"
                "Try: BTC, ETH, SOL, ADA, or /allcoins for full list."
            )
            return

        await update.message.reply_text("🤖 Analyzing market data... Please wait.")

        # Get detailed coin data for AI analysis
        coin_data = await market_service.get_detailed_coin_data(coin_id)
        if not coin_data:
            await update.message.reply_text(
                "❌ Unable to fetch market data right now. Please try again later."
            )
            return

        # Get AI analysis
        ai_analysis = await ai_analyst.should_i_buy_analysis(coin_data)
        
        # Format response
        coin_name = coin_data.get('name', coin_input)
        current_price = coin_data.get('current_price', 0)
        price_change = coin_data.get('price_change_percentage_24h', 0)
        
        response = f"🤖 AI Analysis for {coin_name.upper()}\n\n"
        response += f"💰 Current Price: ${current_price:,.4f}\n"
        response += f"📈 24h Change: {price_change:+.2f}%\n\n"
        response += f"🧠 AI Recommendation:\n{ai_analysis}\n\n"
        response += "⚠️ This is AI-generated advice. Always do your own research!"
        
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error in shouldibuy_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while analyzing. Please try again later."
        )

async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /trending command for trending cryptocurrencies."""
    try:
        await update.message.reply_text("📈 Fetching trending cryptocurrencies...")
        
        trending_coins = await market_service.get_trending_coins()
        if not trending_coins:
            await update.message.reply_text(
                "❌ Unable to fetch trending data right now. Please try again later."
            )
            return

        response = "🔥 Top Trending Cryptocurrencies:\n\n"
        for i, coin in enumerate(trending_coins, 1):
            name = coin.get('name', 'Unknown')
            symbol = coin.get('symbol', '').upper()
            rank = coin.get('market_cap_rank', 'N/A')
            
            response += f"{i}. {name} ({symbol})\n"
            response += f"   📊 Market Cap Rank: #{rank}\n\n"

        response += "💡 Use /shouldibuy [COIN] for AI analysis"
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error in trending_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while fetching trending data."
        )

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /daily command for AI market summary."""
    try:
        await update.message.reply_text("📊 Generating AI market summary...")
        
        # Get top coins for analysis
        top_coins = await market_service.get_top_coins_by_market_cap(15)
        if not top_coins:
            await update.message.reply_text(
                "❌ Unable to fetch market data right now. Please try again later."
            )
            return

        # Generate AI summary
        summary = await ai_analyst.generate_daily_summary(top_coins)
        
        response = f"📊 Daily Market Digest\n\n{summary}\n\n"
        response += "🤖 Powered by AI | 💡 Use /shouldibuy for specific advice"
        
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error in daily_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while generating market summary."
        )

async def setalert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /setalert command for price alerts."""
    try:
        if len(context.args) < 2:
            await update.message.reply_text(
                "🔔 Set Price Alerts\n\n"
                "Usage: /setalert [COIN] [PRICE]\n"
                "Examples:\n"
                "• /setalert BTC 50000\n"
                "• /setalert ethereum 3000\n\n"
                "💡 Get notified when price reaches your target!"
            )
            return

        coin_input = context.args[0].lower()
        try:
            target_price = float(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid price number.")
            return

        if target_price <= 0:
            await update.message.reply_text("❌ Price must be greater than 0.")
            return

        # Map coin to ID
        coin_id = coin_mapper.get_coin_id(coin_input)
        if not coin_id:
            await update.message.reply_text(
                f"❌ Cryptocurrency '{coin_input}' not found!"
            )
            return

        # Get current price to determine alert direction
        current_data = await market_service.get_detailed_coin_data(coin_id)
        if not current_data:
            await update.message.reply_text(
                "❌ Unable to fetch current price. Please try again."
            )
            return

        current_price = current_data.get('current_price', 0)
        coin_symbol = current_data.get('symbol', coin_input).upper()
        coin_name = current_data.get('name', coin_input)
        
        # Determine if alert is for price going above or below
        is_above = target_price > current_price
        direction = "above" if is_above else "below"
        
        # Create alert
        user_id = str(update.effective_user.id)
        success = await alert_service.create_alert(
            user_id, coin_id, coin_symbol, target_price, is_above
        )
        
        if success:
            response = f"🔔 Alert Set Successfully!\n\n"
            response += f"💰 Coin: {coin_name} ({coin_symbol})\n"
            response += f"🎯 Target: ${target_price:,.2f}\n"
            response += f"📈 Current: ${current_price:,.4f}\n"
            response += f"📊 Alert when price goes {direction} target\n\n"
            response += "✅ You'll be notified when triggered!"
        else:
            response = "❌ Failed to create alert. Please try again."
            
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error in setalert_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while setting alert."
        )

async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /alerts command to view user alerts."""
    try:
        user_id = str(update.effective_user.id)
        alerts = await alert_service.get_user_alerts(user_id)
        
        if not alerts:
            await update.message.reply_text(
                "🔔 No Active Alerts\n\n"
                "Set your first alert with:\n"
                "/setalert [COIN] [PRICE]\n\n"
                "Example: /setalert BTC 50000"
            )
            return

        response = f"🔔 Your Active Alerts ({len(alerts)}):\n\n"
        
        for i, alert in enumerate(alerts, 1):
            alert_id = alert['id']
            coin_symbol = alert['coin_symbol']
            target_price = alert['target_price']
            direction = "📈 Above" if alert['is_above'] else "📉 Below"
            created = alert['created_at'].strftime("%b %d")
            
            response += f"{i}. 💰 {coin_symbol} (ID: {alert_id})\n"
            response += f"🎯 ${target_price:,.2f} ({direction})\n"
            response += f"📅 Set: {created}\n\n"

        response += "🗑️ Use /deletealert [ID] to remove alerts\n"
        response += "💡 Alerts auto-delete when triggered"
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error in alerts_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while fetching alerts."
        )

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /chart command to generate price history charts."""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "📈 **Advanced Price Chart Generator**\n\n"
            "Usage: `/chart [COIN] [DAYS] [TYPE]`\n\n"
            "**Examples:**\n"
            "• `/chart BTC` - 7-day line chart\n"
            "• `/chart ETH 30 volume` - 30-day chart with volume\n"
            "• `/chart ADA 7 candlestick` - 7-day chart with indicators\n"
            "• `/chart SOL 1 area` - 24-hour area chart\n\n"
            "**Available periods:** 1, 7, 30, 90, 365 days\n"
            "**Chart types:** line, area, candlestick, volume",
            parse_mode='Markdown'
        )
        return
    
    coin_input = context.args[0].upper()
    
    # Default to 7 days if no period specified
    days = 7
    chart_type = 'line'  # Default chart type
    
    if len(context.args) > 1:
        try:
            days = int(context.args[1])
            if days not in [1, 7, 30, 90, 365]:
                await update.message.reply_text(
                    "❌ Invalid time period!\n\n"
                    "Available periods: 1, 7, 30, 90, 365 days"
                )
                return
        except ValueError:
            await update.message.reply_text("❌ Invalid number format for days!")
            return
    
    # Check for chart type parameter
    if len(context.args) > 2:
        chart_type = context.args[2].lower()
        if chart_type not in ['line', 'area', 'candlestick', 'volume']:
            await update.message.reply_text(
                "❌ Invalid chart type!\n\n"
                "Available types: line, area, candlestick, volume"
            )
            return
    
    # Get coin ID from user input
    coin_id = coin_mapper.get_coin_id(coin_input)
    if not coin_id:
        await update.message.reply_text(
            f"❌ **Coin Not Found**\n\n"
            f"'{coin_input}' is not supported.\n\n"
            f"💡 Use /allcoins to see supported cryptocurrencies"
        )
        return
    
    try:
        # Send "generating chart" message
        chart_type_name = chart_type.title()
        if chart_type == 'volume':
            chart_type_name = "Price & Volume"
        elif chart_type == 'candlestick':
            chart_type_name = "Technical Analysis"
        
        status_message = await update.message.reply_text(
            f"📈 Generating {days}-day {chart_type_name} chart for {coin_input}...\n"
            f"⏳ This may take a few seconds..."
        )
        
        # Generate the chart
        chart_bytes = await chart_service.generate_price_chart(coin_id, coin_input, days, chart_type)
        
        if chart_bytes:
            # Send the chart image
            from io import BytesIO
            chart_file = BytesIO(chart_bytes)
            chart_file.name = f"{coin_input}_{days}d_chart.png"
            
            # Create inline keyboard for chart type switching
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 Line", callback_data=f"chart_{coin_id}_{days}_line"),
                    InlineKeyboardButton("🔵 Area", callback_data=f"chart_{coin_id}_{days}_area"),
                ],
                [
                    InlineKeyboardButton("📈 Technical", callback_data=f"chart_{coin_id}_{days}_candlestick"),
                    InlineKeyboardButton("📊 Volume", callback_data=f"chart_{coin_id}_{days}_volume"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Enhanced caption with chart type info
            chart_info = {
                'line': '📊 Clean price line chart',
                'area': '🔵 Filled area chart',
                'candlestick': '📈 Technical analysis with moving averages',
                'volume': '📊 Price chart with trading volume'
            }
            
            await update.message.reply_photo(
                photo=chart_file,
                caption=f"📈 **{coin_input.upper()} {chart_type_name} Chart ({days} Days)**\n\n"
                       f"{chart_info[chart_type]}\n"
                       f"Generated with live market data from CoinGecko\n\n"
                       f"💡 *Try different chart types using the buttons below*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Delete the status message
            await status_message.delete()
            
        else:
            await status_message.edit_text(
                f"❌ **Chart Generation Failed**\n\n"
                f"Unable to generate chart for {coin_input}.\n"
                f"This might be due to insufficient price data."
            )
            
    except Exception as e:
        logger.error(f"Error in chart_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while generating the chart. Please try again."
        )

async def delete_alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /deletealert command to delete a specific alert."""
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "❌ Invalid format!\n\n"
            "Usage: /deletealert [ALERT_ID]\n\n"
            "💡 Use /alerts to see your alert IDs\n"
            "Example: /deletealert 123"
        )
        return
    
    user_id = str(update.effective_user.id)
    
    try:
        alert_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid alert ID! Please enter a valid number.")
        return
    
    try:
        success = await alert_service.delete_alert(user_id, alert_id)
        
        if success:
            await update.message.reply_text(
                f"✅ **Alert Deleted!**\n\n"
                f"🗑️ Alert ID {alert_id} has been removed successfully.\n\n"
                f"📱 Use /alerts to view your remaining alerts",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ **Alert Not Found**\n\n"
                f"Alert ID {alert_id} doesn't exist or doesn't belong to you.\n\n"
                f"💡 Use /alerts to see your active alerts"
            )
            
    except Exception as e:
        logger.error(f"Error in delete_alert_command: {e}")
        await update.message.reply_text("❌ Error deleting alert. Please try again.")

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /portfolio command to check wallet holdings."""
    try:
        user_id = str(update.effective_user.id)
        
        # If no args provided, try to use default wallet
        if not context.args:
            default_wallet = await wallet_service.get_default_wallet(user_id)
            if default_wallet:
                chain = default_wallet['blockchain']
                wallet_address = default_wallet['address']
                await update.message.reply_text(
                    f"🔍 Using your default wallet ({wallet_service.truncate_address(wallet_address)}) on {chain.upper()}..."
                )
            else:
                await update.message.reply_text(
                    "💼 Portfolio Tracker\n\n"
                    "Usage: /portfolio [WALLET_ADDRESS]\n"
                    "Optional: /portfolio [CHAIN] [WALLET_ADDRESS]\n\n"
                    "Examples:\n"
                    "• /portfolio 0x742d35Cc6634C0532925a3b844Bc454e4438f44e\n"
                    "• /portfolio bsc 0x742d35Cc6634C0532925a3b844Bc454e4438f44e\n\n"
                    "💡 Set a default wallet with /setwallet [WALLET_ADDRESS]\n"
                    "Supported chains: eth, bsc, polygon, avalanche, arbitrum"
                )
                return

        # Parse arguments (chain + wallet or just wallet)
        if len(context.args) == 1:
            chain = 'eth'  # Default to Ethereum
            wallet_address = context.args[0]
        elif len(context.args) == 2:
            chain = context.args[0].lower()
            wallet_address = context.args[1]
        elif len(context.args) > 2:
            await update.message.reply_text(
                "❌ Invalid format. Use:\n"
                "/portfolio [WALLET_ADDRESS]\n"
                "or /portfolio [CHAIN] [WALLET_ADDRESS]"
            )
            return
        # If we reach here and no args but no default wallet, we already returned above

        # Validate wallet address format
        is_valid, address_type = portfolio_service.validate_wallet_address(wallet_address)
        if not is_valid:
            if address_type == "tron":
                await update.message.reply_text(
                    "❌ TRON addresses are not supported yet!\n\n"
                    "Currently supported: Ethereum-compatible addresses only\n"
                    "• Ethereum (ETH)\n"
                    "• Binance Smart Chain (BSC)\n"
                    "• Polygon (MATIC)\n"
                    "• Avalanche (AVAX)\n"
                    "• Arbitrum\n\n"
                    "Example: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
                )
            elif address_type == "bitcoin":
                await update.message.reply_text(
                    "❌ Bitcoin addresses are not supported yet!\n\n"
                    "Currently supported: Ethereum-compatible addresses only\n"
                    "Example: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
                )
            else:
                await update.message.reply_text(
                    "❌ Invalid wallet address format!\n\n"
                    "Please provide a valid Ethereum-compatible address:\n"
                    "• Must start with 0x\n"
                    "• Must be 42 characters long\n"
                    "• Example: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
                )
            return

        # Check if chain is supported
        chain_info = portfolio_service.get_chain_info(chain)
        if not chain_info:
            await update.message.reply_text(
                f"❌ Unsupported blockchain: {chain}\n\n"
                "Supported chains:\n"
                "• eth (Ethereum)\n"
                "• bsc (Binance Smart Chain)\n"
                "• polygon (Polygon)\n"
                "• avalanche (Avalanche)\n"
                "• arbitrum (Arbitrum)"
            )
            return

        await update.message.reply_text(f"📊 Fetching portfolio from {chain_info['name']}...")

        # Fetch portfolio data
        portfolio_data = await portfolio_service.get_wallet_portfolio(wallet_address, chain)
        
        if not portfolio_data:
            await update.message.reply_text(
                "❌ Unable to fetch portfolio data. Please try again later."
            )
            return

        if 'error' in portfolio_data:
            error_message = portfolio_data['error']
            if 'authentication failed' in error_message.lower():
                await update.message.reply_text(
                    "❌ Portfolio service temporarily unavailable.\n"
                    "Please try again later."
                )
            else:
                await update.message.reply_text(f"❌ {error_message}")
            return

        # Format and send portfolio response
        response = format_portfolio_message(portfolio_data)
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error in portfolio_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while fetching portfolio data."
        )

def format_portfolio_message(portfolio_data: dict) -> str:
    """Format portfolio data into a user-friendly message."""
    try:
        address = portfolio_data.get('address', '')
        chain = portfolio_data.get('chain', 'Unknown')
        tokens = portfolio_data.get('tokens', [])
        total_value = portfolio_data.get('total_value', 0)
        
        # Truncate address for display
        short_address = f"{address[:6]}...{address[-4:]}" if len(address) > 10 else address
        
        if not tokens:
            return f"📊 Portfolio Overview\n\n💼 Address: {short_address}\n🔗 Chain: {chain}\n\n💰 No tokens found or all balances below $0.01"

        response = f"📊 Portfolio Overview\n\n💼 Address: {short_address}\n🔗 Chain: {chain}\n\n"
        
        # Show top tokens (limit to prevent message being too long)
        display_tokens = tokens[:10]  # Show top 10 tokens
        
        for i, token in enumerate(display_tokens, 1):
            name = token.get('name', 'Unknown')
            symbol = token.get('symbol', '')
            balance = token.get('balance', 0)
            value_usd = token.get('value_usd', 0)
            price_change_24h = token.get('price_change_24h', 0)
            
            # Format balance display
            if balance >= 1:
                balance_str = f"{balance:,.2f}"
            else:
                balance_str = f"{balance:.6f}".rstrip('0').rstrip('.')
            
            # Price change indicator
            if price_change_24h > 0:
                change_icon = "📈"
                change_str = f"+{price_change_24h:.1f}%"
            elif price_change_24h < 0:
                change_icon = "📉"
                change_str = f"{price_change_24h:.1f}%"
            else:
                change_icon = "➡️"
                change_str = "0.0%"
            
            response += f"{i}. {symbol}: {balance_str} → ${value_usd:,.2f} {change_icon}\n"
        
        if len(tokens) > 10:
            response += f"\n... and {len(tokens) - 10} more tokens\n"
        
        response += f"\n💰 Total Value: ${total_value:,.2f}\n"
        response += f"📈 Tokens: {len(tokens)}\n"
        response += "\n💡 Use /shouldibuy [TOKEN] for AI analysis"
        
        return response
        
    except Exception as e:
        logger.error(f"Error formatting portfolio message: {e}")
        return "❌ Error formatting portfolio data."

async def setcurrency_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /setcurrency command to set preferred currencies."""
    try:
        if not context.args:
            # Show available currencies with inline keyboard
            message = (
                "💱 *Set Your Preferred Currencies*\n\n"
                "Choose up to 5 currencies for price display:\n\n"
                "🇺🇸 USD - US Dollar\n"
                "🇪🇺 EUR - Euro\n"
                "🇬🇧 GBP - British Pound\n"
                "🇯🇵 JPY - Japanese Yen\n"
                "🇨🇦 CAD - Canadian Dollar\n"
                "🇦🇺 AUD - Australian Dollar\n"
                "🇨🇭 CHF - Swiss Franc\n"
                "🇨🇳 CNY - Chinese Yuan\n"
                "🇮🇳 INR - Indian Rupee\n"
                "🇰🇷 KRW - South Korean Won\n"
                "🇸🇬 SGD - Singapore Dollar\n"
                "🇭🇰 HKD - Hong Kong Dollar\n"
                "🇳🇿 NZD - New Zealand Dollar\n"
                "🇸🇪 SEK - Swedish Krona\n"
                "🇳🇴 NOK - Norwegian Krone\n"
                "🇩🇰 DKK - Danish Krone\n"
                "🇵🇱 PLN - Polish Zloty\n"
                "🇷🇺 RUB - Russian Ruble\n"
                "🇧🇷 BRL - Brazilian Real\n"
                "🇲🇽 MXN - Mexican Peso\n"
                "🇿🇦 ZAR - South African Rand\n"
                "🇹🇷 TRY - Turkish Lira\n"
                "🇦🇪 AED - UAE Dirham\n"
                "🇸🇦 SAR - Saudi Riyal\n\n"
                "Usage: `/setcurrency usd eur inr`\n"
                "Current: USD, EUR, INR"
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        # Validate and set currencies
        requested_currencies = [currency.lower() for currency in context.args]
        
        # Check if currencies are supported
        invalid_currencies = [c for c in requested_currencies if c not in SUPPORTED_CURRENCIES]
        if invalid_currencies:
            await update.message.reply_text(
                f"❌ Unsupported currencies: {', '.join(invalid_currencies).upper()}\n\n"
                "Use `/setcurrency` to see all supported currencies."
            )
            return
        
        # Limit to 5 currencies max
        if len(requested_currencies) > 5:
            await update.message.reply_text(
                "❌ Maximum 5 currencies allowed.\n"
                "Please select up to 5 currencies."
            )
            return
        
        # Store user preferences (in a real app, this would be saved to database)
        user_id = str(update.effective_user.id)
        
        # For now, we'll store in context.user_data
        if 'user_currencies' not in context.user_data:
            context.user_data['user_currencies'] = {}
        
        context.user_data['user_currencies'][user_id] = requested_currencies
        
        # Format success message
        currency_names = []
        for currency in requested_currencies:
            flag = {
                'usd': '🇺🇸', 'eur': '🇪🇺', 'gbp': '🇬🇧', 'jpy': '🇯🇵',
                'cad': '🇨🇦', 'aud': '🇦🇺', 'chf': '🇨🇭', 'cny': '🇨🇳',
                'inr': '🇮🇳', 'krw': '🇰🇷', 'sgd': '🇸🇬', 'hkd': '🇭🇰',
                'nzd': '🇳🇿', 'sek': '🇸🇪', 'nok': '🇳🇴', 'dkk': '🇩🇰',
                'pln': '🇵🇱', 'rub': '🇷🇺', 'brl': '🇧🇷', 'mxn': '🇲🇽',
                'zar': '🇿🇦', 'try': '🇹🇷', 'aed': '🇦🇪', 'sar': '🇸🇦'
            }.get(currency, '🌍')
            currency_names.append(f"{flag} {currency.upper()}")
        
        await update.message.reply_text(
            f"✅ *Currency Preferences Updated*\n\n"
            f"Your selected currencies:\n{', '.join(currency_names)}\n\n"
            f"All price commands will now show prices in these currencies.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in setcurrency command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while setting currencies.\n"
            "Please try again later."
        )

async def totalusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /totalusers command for viewing bot user statistics (admin only)."""
    try:
        user_id = str(update.effective_user.id)
        
        # Check if user is authorized admin
        if not user_service.is_admin_user(user_id):
            await update.message.reply_text(
                "❌ Access denied. This command is restricted to authorized administrators only."
            )
            return
        
        # Send loading message
        loading_msg = await update.message.reply_text("📊 Generating user statistics...")
        
        # Get user statistics
        stats = await user_service.get_total_users()
        
        # Format and send the statistics
        message = user_service.format_user_stats(stats)
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in totalusers command: {e}")
        await update.message.reply_text("❌ An error occurred while generating user statistics.")

async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /convert command for currency conversion with real-time rates."""
    try:
        if not context.args or len(context.args) < 3:
            await update.message.reply_text(
                """
💱 **Currency Converter**

**Usage:** `/convert [AMOUNT] [FROM] [TO]`

**Examples:**
• `/convert 100 usd eur` - Convert $100 to EUR
• `/convert 50 eur gbp` - Convert €50 to GBP  
• `/convert 1000 jpy usd` - Convert ¥1000 to USD

**Supported:** USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR, KRW, SGD, HKD, NZD, SEK, NOK, DKK, PLN, RUB, BRL, MXN, ZAR, TRY, AED, SAR

💡 All rates are live and updated in real-time.
"""
            )
            return
        
        # Parse arguments
        try:
            amount = float(context.args[0])
            from_currency = context.args[1].upper()
            to_currency = context.args[2].upper()
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ Invalid format. Use: `/convert [AMOUNT] [FROM] [TO]`\n"
                "Example: `/convert 100 usd eur`"
            )
            return
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be greater than 0.")
            return
        
        # Send loading message
        loading_msg = await update.message.reply_text("💱 Converting currencies...")
        
        # Perform conversion
        conversion = await currency_converter.convert_currency(amount, from_currency, to_currency)
        
        if not conversion:
            await loading_msg.edit_text("❌ Unable to fetch current exchange rates. Please try again later.")
            return
        
        if 'error' in conversion:
            await loading_msg.edit_text(f"❌ {conversion['error']}")
            return
        
        # Format result
        result_text = currency_converter.format_conversion_result(conversion)
        
        # Add timestamp if available
        if conversion.get('timestamp'):
            result_text += f"\n🕐 Updated: {conversion['timestamp']}"
        
        # Create quick conversion buttons for popular pairs
        keyboard = []
        if from_currency != to_currency:
            # Reverse conversion button
            reverse_amount = conversion['converted_amount']
            if reverse_amount > 0:
                keyboard.append([
                    InlineKeyboardButton(
                        f"🔄 Convert {to_currency} → {from_currency}",
                        callback_data=f"convert_{reverse_amount:.2f}_{to_currency}_{from_currency}"
                    )
                ])
        
        # Add more conversion options
        popular_targets = ['USD', 'EUR', 'GBP', 'JPY']
        if from_currency in popular_targets:
            popular_targets.remove(from_currency)
        if to_currency in popular_targets:
            popular_targets.remove(to_currency)
        
        if popular_targets:
            quick_buttons = []
            for target in popular_targets[:2]:  # Limit to 2 buttons
                quick_buttons.append(
                    InlineKeyboardButton(
                        f"→ {target}",
                        callback_data=f"convert_{amount}_{from_currency}_{target}"
                    )
                )
            if quick_buttons:
                keyboard.append(quick_buttons)
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await loading_msg.edit_text(result_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in convert command: {e}")
        await update.message.reply_text("❌ An error occurred while converting currencies.")

async def setwallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /setwallet command to save default wallet."""
    try:
        user_id = str(update.effective_user.id)
        
        if not context.args:
            await update.message.reply_text(
                "💳 Set Default Wallet\n\n"
                "Usage: /setwallet [WALLET_ADDRESS]\n"
                "Optional: /setwallet [CHAIN] [WALLET_ADDRESS] [LABEL]\n\n"
                "Examples:\n"
                "• /setwallet 0x742d35Cc6634C0532925a3b844Bc454e4438f44e\n"
                "• /setwallet bsc 0x742d35Cc6634C0532925a3b844Bc454e4438f44e MyWallet\n\n"
                "Supported chains: eth, bsc, polygon, avalanche, arbitrum"
            )
            return
        
        # Parse arguments
        if len(context.args) == 1:
            chain = 'eth'  # Default to Ethereum
            wallet_address = context.args[0]
            label = None
        elif len(context.args) == 2:
            # Could be chain + wallet or wallet + label
            if context.args[0].lower() in ['eth', 'bsc', 'polygon', 'avalanche', 'arbitrum']:
                chain = context.args[0].lower()
                wallet_address = context.args[1]
                label = None
            else:
                chain = 'eth'
                wallet_address = context.args[0]
                label = context.args[1]
        elif len(context.args) == 3:
            chain = context.args[0].lower()
            wallet_address = context.args[1]
            label = context.args[2]
        else:
            await update.message.reply_text(
                "❌ Invalid format. Use:\n"
                "/setwallet [WALLET_ADDRESS]\n"
                "or /setwallet [CHAIN] [WALLET_ADDRESS] [LABEL]"
            )
            return
        
        # Validate wallet address format
        is_valid, address_type = portfolio_service.validate_wallet_address(wallet_address)
        if not is_valid:
            if address_type == "tron":
                await update.message.reply_text(
                    "❌ TRON addresses are not supported yet!\n\n"
                    "Currently supported: Ethereum-compatible addresses only\n"
                    "Example: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
                )
            elif address_type == "bitcoin":
                await update.message.reply_text(
                    "❌ Bitcoin addresses are not supported yet!\n\n"
                    "Currently supported: Ethereum-compatible addresses only\n"
                    "Example: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
                )
            else:
                await update.message.reply_text(
                    "❌ Invalid wallet address format!\n\n"
                    "Please provide a valid Ethereum-compatible address:\n"
                    "• Must start with 0x\n"
                    "• Must be 42 characters long\n"
                    "• Example: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
                )
            return
        
        # Check if chain is supported
        chain_info = portfolio_service.get_chain_info(chain)
        if not chain_info:
            await update.message.reply_text(
                f"❌ Unsupported chain: {chain}\n\n"
                "Supported chains: eth, bsc, polygon, avalanche, arbitrum"
            )
            return
        
        # Save the wallet
        success = await wallet_service.set_default_wallet(user_id, wallet_address, chain, label)
        
        if success:
            truncated_address = wallet_service.truncate_address(wallet_address)
            chain_name = chain_info['name']
            
            message = f"✅ Default wallet saved!\n\n"
            message += f"🔗 Chain: {chain_name}\n"
            message += f"📍 Address: {truncated_address}\n"
            
            if label:
                message += f"🏷️ Label: {label}\n"
            
            message += f"\n💡 Use /portfolio to check your holdings anytime!"
            
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ Failed to save wallet. Please try again.")
    
    except Exception as e:
        logger.error(f"Error in setwallet_command: {e}")
        await update.message.reply_text("❌ An error occurred while saving wallet.")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the Quick Actions menu with inline keyboard."""
    user_id = str(update.effective_user.id)
    logger.info(f"Menu command requested by user {user_id}")
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Bitcoin Price", callback_data="quick_price_bitcoin"),
            InlineKeyboardButton("📈 Ethereum Price", callback_data="quick_price_ethereum"),
        ],
        [
            InlineKeyboardButton("🔥 Trending Coins", callback_data="quick_trending"),
            InlineKeyboardButton("📊 My Portfolio", callback_data="quick_portfolio"),
        ],
        [
            InlineKeyboardButton("🤖 AI Analysis", callback_data="quick_ai_menu"),
            InlineKeyboardButton("🔔 My Alerts", callback_data="quick_alerts"),
        ],
        [
            InlineKeyboardButton("🎮 Crypto Quiz", callback_data="quick_quiz"),
            InlineKeyboardButton("📱 More Commands", callback_data="quick_help"),
        ],
        [
            InlineKeyboardButton("🔄 Refresh Menu", callback_data="quick_refresh"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚡ **Quick Actions Menu**\n\n"
        "Choose an action below for instant results:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def quick_ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display AI analysis submenu."""
    keyboard = [
        [
            InlineKeyboardButton("🤖 Should I Buy Bitcoin?", callback_data="quick_ai_bitcoin"),
            InlineKeyboardButton("🤖 Should I Buy Ethereum?", callback_data="quick_ai_ethereum"),
        ],
        [
            InlineKeyboardButton("📝 Daily Market Summary", callback_data="quick_daily"),
            InlineKeyboardButton("🔍 Custom Analysis", callback_data="quick_custom_ai"),
        ],
        [
            InlineKeyboardButton("⬅️ Back to Menu", callback_data="quick_refresh"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "🤖 **AI Analysis Menu**\n\n"
            "Get intelligent crypto insights:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "🤖 **AI Analysis Menu**\n\n"
            "Get intelligent crypto insights:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /recommend command for personalized investment recommendations."""
    try:
        user_id = str(update.effective_user.id)
        
        await update.message.reply_text("🎯 Analyzing your profile and generating personalized recommendations...")
        
        # Generate personalized recommendations
        recommendations = await recommendation_engine.generate_personalized_recommendations(user_id)
        
        if "error" in recommendations:
            await update.message.reply_text(
                "❌ Unable to generate recommendations. Please set up alerts or wallet for better insights."
            )
            return
        
        # Format recommendations message
        response = "🎯 **Your Personalized Investment Recommendations**\n\n"
        response += f"📊 Risk Profile: {recommendations['user_risk_profile'].title()}\n"
        response += f"📈 Market Sentiment: {recommendations['market_sentiment'].title()}\n\n"
        
        recs = recommendations.get("recommendations", [])
        if recs:
            for i, rec in enumerate(recs[:3], 1):  # Show top 3 recommendations
                response += f"**{i}. {rec['title']}**\n"
                response += f"{rec['description']}\n"
                
                if rec.get("suggested_coins"):
                    coins = ", ".join(rec["suggested_coins"][:3])
                    response += f"💰 Consider: {coins}\n"
                
                response += f"🎯 Priority: {rec.get('priority', 'medium').title()}\n"
                response += f"💡 {rec.get('reasoning', '')}\n\n"
        else:
            response += "📝 Set up price alerts and wallet to get personalized recommendations!\n\n"
        
        response += "💡 Use /insights for detailed market analysis\n"
        response += "🛡️ Use /riskprofile to understand your investment style"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in recommend_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while generating recommendations."
        )

async def insights_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /insights command for market insights based on user profile."""
    try:
        user_id = str(update.effective_user.id)
        
        await update.message.reply_text("📈 Generating market insights based on your profile...")
        
        # Generate personalized recommendations to get insights
        recommendations = await recommendation_engine.generate_personalized_recommendations(user_id)
        
        if "error" in recommendations:
            await update.message.reply_text(
                "❌ Unable to generate insights. Please set up alerts or wallet for better analysis."
            )
            return
        
        # Get portfolio analysis
        portfolio_analysis = recommendations.get("portfolio_analysis", {})
        
        response = "📈 **Market Insights for Your Profile**\n\n"
        response += f"🎯 Your Investment Style: {recommendations.get('user_risk_profile', 'moderate').title()}\n"
        response += f"📊 Market Sentiment: {recommendations.get('market_sentiment', 'neutral').title()}\n\n"
        
        # Portfolio insights
        if portfolio_analysis:
            total_value = portfolio_analysis.get("total_value", 0)
            diversification = portfolio_analysis.get("diversification", "unknown")
            
            response += "💼 **Portfolio Analysis:**\n"
            if total_value > 0:
                response += f"💰 Total Value: ${total_value:,.2f}\n"
            response += f"🌐 Diversification: {diversification.title()}\n"
            
            top_holdings = portfolio_analysis.get("top_holdings", [])
            if top_holdings:
                response += f"🏆 Top Holdings: {', '.join(top_holdings)}\n"
            response += "\n"
        
        # Market recommendations
        recs = recommendations.get("recommendations", [])
        if recs:
            response += "🎯 **Key Insights:**\n"
            for rec in recs[:2]:  # Show top 2 insights
                response += f"• {rec.get('reasoning', 'Market analysis available')}\n"
            response += "\n"
        
        response += "💡 Use /recommend for specific investment suggestions\n"
        response += "📊 Use /shouldibuy [COIN] for detailed AI analysis"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in insights_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while generating insights."
        )

async def riskprofile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /riskprofile command to analyze user's risk tolerance."""
    try:
        user_id = str(update.effective_user.id)
        
        await update.message.reply_text("🛡️ Analyzing your risk profile...")
        
        # Generate user profile analysis
        recommendations = await recommendation_engine.generate_personalized_recommendations(user_id)
        
        if "error" in recommendations:
            await update.message.reply_text(
                "❌ Unable to analyze risk profile. Please set up alerts or wallet for analysis."
            )
            return
        
        risk_level = recommendations.get("user_risk_profile", "moderate")
        portfolio_analysis = recommendations.get("portfolio_analysis", {})
        
        response = "🛡️ **Your Risk Profile Analysis**\n\n"
        response += f"📊 Risk Level: **{risk_level.title()}**\n\n"
        
        # Risk level descriptions
        if risk_level == "conservative":
            response += "🔒 **Conservative Investor**\n"
            response += "• You prefer stable, established cryptocurrencies\n"
            response += "• Lower volatility tolerance\n"
            response += "• Focus on long-term value preservation\n"
            response += "• Recommended: BTC, ETH, stablecoins\n\n"
        elif risk_level == "aggressive":
            response += "🚀 **Aggressive Investor**\n"
            response += "• You're comfortable with high volatility\n"
            response += "• Seeking high growth potential\n"
            response += "• Active trading approach\n"
            response += "• Recommended: Altcoins, emerging projects\n\n"
        else:
            response += "⚖️ **Moderate Investor**\n"
            response += "• Balanced approach to risk and reward\n"
            response += "• Mix of established and emerging assets\n"
            response += "• Moderate volatility tolerance\n"
            response += "• Recommended: Diversified portfolio\n\n"
        
        # Portfolio-based insights
        if portfolio_analysis:
            diversification = portfolio_analysis.get("diversification", "unknown")
            num_tokens = portfolio_analysis.get("num_tokens", 0)
            
            response += "💼 **Portfolio Risk Assessment:**\n"
            response += f"🌐 Diversification: {diversification.title()}\n"
            
            if num_tokens > 0:
                response += f"📊 Number of Holdings: {num_tokens}\n"
                
                if diversification == "low":
                    response += "⚠️ Consider adding more assets to reduce risk\n"
                elif diversification == "high":
                    response += "✅ Well-diversified portfolio\n"
            response += "\n"
        
        response += "💡 **Recommendations:**\n"
        response += "• Use /recommend for personalized investment advice\n"
        response += "• Set price alerts to match your risk tolerance\n"
        response += "• Regular portfolio rebalancing recommended"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in riskprofile_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while analyzing risk profile."
        )

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /quiz command to start educational quiz."""
    user_id = str(update.effective_user.id)
    
    # Check if user has an active quiz session
    if quiz_service.has_active_session(user_id):
        current_question = quiz_service.get_current_question(user_id)
        if current_question and "error" not in current_question:
            await send_quiz_question(update, current_question)
            return
        else:
            quiz_service.end_session(user_id)
    
    # Get difficulty level from command arguments
    difficulty = "beginner"  # default
    if context.args and len(context.args) > 0:
        difficulty_input = context.args[0].lower()
        if difficulty_input in ["beginner", "intermediate", "advanced"]:
            difficulty = difficulty_input
    
    # Start new quiz
    try:
        question_data = quiz_service.start_quiz(user_id, difficulty)
        if question_data and "error" not in question_data:
            await send_quiz_question(update, question_data)
        else:
            await update.message.reply_text(
                "❌ Sorry, I couldn't start the quiz. Please try again with /quiz [difficulty].\n"
                "Available difficulties: beginner, intermediate, advanced"
            )
    except Exception as e:
        logger.error(f"Error starting quiz for user {user_id}: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again later.")

async def send_quiz_question(update: Update, question_data: Dict) -> None:
    """Send quiz question with inline keyboard."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    question_text = f"""🎮 **Crypto Quiz - {question_data['difficulty'].title()} Level**

📝 **Question {question_data['question_number']}/{question_data['total_questions']}**

{question_data['question']}

Choose your answer:"""
    
    # Create inline keyboard with answer options
    keyboard = []
    for i, option in enumerate(question_data['options']):
        keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option}", callback_data=f"quiz_answer_{i}")])
    
    # Add quit option
    keyboard.append([InlineKeyboardButton("❌ Quit Quiz", callback_data="quiz_quit")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(question_text, reply_markup=reply_markup, parse_mode='Markdown')

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /scan command for multi-chain token analysis."""
    user_id = str(update.effective_user.id)
    logger.info(f"Scan command requested by user {user_id}")
    
    # Check arguments
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "🔍 **Token Scanner**\n\n"
            "**Usage:** `/scan [CHAIN] [TOKEN_ADDRESS]`\n\n"
            "**Supported Chains:**\n"
            "• `ETH` - Ethereum\n"
            "• `BNB` - BNB Smart Chain\n"
            "• `SOL` - Solana\n"
            "• `BASE` - Base\n"
            "• `SUI` - Sui\n\n"
            "**Example:**\n"
            "`/scan ETH 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984`\n\n"
            "Get comprehensive token analysis with AI-powered risk assessment!",
            parse_mode='Markdown'
        )
        return
    
    chain = context.args[0].upper()
    token_address = context.args[1].strip()
    
    # Validate chain
    supported_chains = ['ETH', 'BNB', 'SOL', 'BASE', 'SUI']
    if chain not in supported_chains:
        await update.message.reply_text(
            f"❌ Unsupported chain: {chain}\n\n"
            f"Supported chains: {', '.join(supported_chains)}"
        )
        return
    
    # Validate address format (basic check)
    if len(token_address) < 32:
        await update.message.reply_text(
            "❌ Invalid token address format. Please provide a valid contract address."
        )
        return
    
    # Send scanning message
    scanning_message = await update.message.reply_text(
        f"🔍 **Scanning Token...**\n\n"
        f"Chain: {chain}\n"
        f"Address: `{token_address[:10]}...{token_address[-8:]}`\n\n"
        f"⏳ Fetching data from multiple sources...",
        parse_mode='Markdown'
    )
    
    try:
        # Scan token
        token_data = await token_scanner.scan_token(chain.lower(), token_address)
        
        if not token_data:
            await scanning_message.edit_text(
                f"❌ **Token Not Found**\n\n"
                f"Could not find token data for:\n"
                f"Chain: {chain}\n"
                f"Address: `{token_address[:10]}...{token_address[-8:]}`\n\n"
                f"Please verify the address and chain are correct.",
                parse_mode='Markdown'
            )
            return
        
        # Update message with basic info
        await scanning_message.edit_text(
            f"🔍 **Analyzing Token Risk...**\n\n"
            f"Found: {token_data.name} ({token_data.symbol})\n"
            f"Chain: {token_data.chain}\n\n"
            f"⏳ Running AI risk assessment...",
            parse_mode='Markdown'
        )
        
        # Get AI risk analysis
        risk_analysis = await risk_analyzer.analyze_token_risk(token_data)
        
        # Format comprehensive report
        report = token_scanner.format_token_report(token_data)
        
        # Add AI risk assessment
        ai_section = f"\n🤖 **AI Risk Assessment:**\n"
        ai_section += f"• **Risk Level:** {risk_analysis['risk_level']}\n"
        ai_section += f"• **Analysis:** {risk_analysis['explanation']}\n"
        
        final_report = report + ai_section
        
        # Send final report
        await scanning_message.edit_text(final_report, parse_mode='Markdown')
        
        logger.info(f"Token scan completed for {token_data.symbol} on {chain}")
        
    except Exception as e:
        logger.error(f"Error in scan command: {e}")
        await scanning_message.edit_text(
            f"❌ **Scan Failed**\n\n"
            f"An error occurred while scanning the token.\n"
            f"Please try again later or contact support if the issue persists.\n\n"
            f"Chain: {chain}\n"
            f"Address: `{token_address[:10]}...{token_address[-8:]}`",
            parse_mode='Markdown'
        )

async def createwallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /createwallet command to generate a new multi-chain wallet."""
    user_id = str(update.effective_user.id)
    
    try:
        await update.message.reply_text("🔐 Generating your multi-chain wallet...")
        
        wallet_data = await multi_wallet_service.create_wallet(user_id)
        
        if "error" in wallet_data:
            await update.message.reply_text(f"❌ {wallet_data['error']}")
            return
        
        # Show addresses first
        addresses = wallet_data["addresses"]
        wallet_message = f"""🔐 **Your Multi-Chain Wallet Created!**

🌐 **Addresses:**
• **ETH/BSC/MATIC:** `{addresses['ethereum']}`
• **Solana:** `{addresses['solana']}`
• **Tron:** `{addresses['tron']}`

⚠️ **IMPORTANT SECURITY WARNING:**
Your 12-word seed phrase will be sent in the next message.
**NEVER share this with anyone!** Keep it safe and private.

💡 Use /mywallet to view your addresses anytime
💡 Use /receive to get QR codes for receiving funds"""
        
        await update.message.reply_text(wallet_message, parse_mode='Markdown')
        
        # Send seed phrase in a separate message with strong warning
        seed_message = f"""🔑 **YOUR SEED PHRASE (KEEP SECRET!):**

`{wallet_data['mnemonic']}`

⚠️ **CRITICAL SECURITY NOTES:**
• Write this down on paper and store it safely
• Anyone with this phrase can access your funds
• Never share it with anyone, not even support
• Delete this message after backing it up
• This is the ONLY way to recover your wallet"""
        
        await update.message.reply_text(seed_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in createwallet command: {e}")
        await update.message.reply_text("❌ Failed to create wallet. Please try again.")

async def mywallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /mywallet command to show wallet addresses and balances."""
    user_id = str(update.effective_user.id)
    
    try:
        await update.message.reply_text("🔍 Loading your wallet information...")
        
        wallet = await multi_wallet_service.get_wallet(user_id)
        if not wallet:
            await update.message.reply_text(
                "❌ No wallet found! Create one first with /createwallet"
            )
            return
        
        # Get balances
        balances = await multi_wallet_service.get_wallet_balances(user_id)
        
        addresses = wallet["addresses"]
        message = "🔐 **Your Multi-Chain Wallet**\n\n"
        
        if balances:
            # Show addresses with balances
            eth_balance = balances.get("ethereum", {})
            bsc_balance = balances.get("bsc", {})
            matic_balance = balances.get("polygon", {})
            sol_balance = balances.get("solana", {})
            trx_balance = balances.get("tron", {})
            
            message += f"""💰 **Balances & Addresses:**

🔹 **Ethereum**
• Address: `{addresses['ethereum']}`
• Balance: {eth_balance.get('balance', 'Error')} {eth_balance.get('symbol', 'ETH')}

🔹 **BSC (Binance Smart Chain)**
• Address: `{addresses['bsc']}`
• Balance: {bsc_balance.get('balance', 'Error')} {bsc_balance.get('symbol', 'BNB')}

🔹 **Polygon**
• Address: `{addresses['polygon']}`
• Balance: {matic_balance.get('balance', 'Error')} {matic_balance.get('symbol', 'MATIC')}

🔹 **Solana**
• Address: `{addresses['solana']}`
• Balance: {sol_balance.get('balance', 'Error')} {sol_balance.get('symbol', 'SOL')}

🔹 **Tron**
• Address: `{addresses['tron']}`
• Balance: {trx_balance.get('balance', 'Error')} {trx_balance.get('symbol', 'TRX')}"""
        else:
            message += f"""📍 **Your Addresses:**

🔹 **ETH/BSC/MATIC:** `{addresses['ethereum']}`
🔹 **Solana:** `{addresses['solana']}`
🔹 **Tron:** `{addresses['tron']}`

💡 Balances will load in future updates"""
        
        message += "\n\n💡 Use /receive to get QR codes for receiving funds"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in mywallet command: {e}")
        await update.message.reply_text("❌ Failed to load wallet. Please try again.")

async def receive_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /receive command to show addresses with QR codes."""
    user_id = str(update.effective_user.id)
    
    try:
        wallet = await multi_wallet_service.get_wallet(user_id)
        if not wallet:
            await update.message.reply_text(
                "❌ No wallet found! Create one first with /createwallet"
            )
            return
        
        addresses = wallet["addresses"]
        
        message = f"""📱 **Receive Crypto**

Copy the address for the network you want to receive on:

🔹 **Ethereum/BSC/Polygon:**
`{addresses['ethereum']}`

🔹 **Solana:**
`{addresses['solana']}`

🔹 **Tron:**
`{addresses['tron']}`

⚠️ **Important:** Make sure to use the correct network when sending funds!
• ETH, USDT-ERC20, etc. → Use Ethereum address
• BNB, USDT-BEP20, etc. → Use BSC address (same as ETH)
• MATIC, USDT-Polygon, etc. → Use Polygon address (same as ETH)
• SOL, USDT-SPL, etc. → Use Solana address
• TRX, USDT-TRC20, etc. → Use Tron address"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in receive command: {e}")
        await update.message.reply_text("❌ Failed to load addresses. Please try again.")

async def quizstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /quizstats command to show user quiz statistics."""
    user_id = str(update.effective_user.id)
    
    try:
        stats = quiz_service.get_quiz_stats(user_id)
        stats_message = f"""📊 **Your Quiz Statistics**

🎯 **Performance:**
• Total Quizzes: {stats['total_quizzes']}
• Average Score: {stats['average_score']:.1f}%
• Best Score: {stats['best_score']}%
• Accuracy: {stats['accuracy']:.1f}%

📚 **Learning Progress:**
• Favorite Difficulty: {stats['favorite_difficulty'].title()}
• Questions Answered: {stats['total_questions_answered']}

🏆 **Want to improve?** Try `/quiz advanced` for a challenge!"""
        
        await update.message.reply_text(stats_message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error getting quiz stats for user {user_id}: {e}")
        await update.message.reply_text("❌ Couldn't retrieve your quiz statistics. Try taking a quiz first with /quiz!")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries from inline keyboards."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == "quick_refresh":
            # Animated loading sequence for refresh
            loading_states = [
                "🔄 Refreshing menu",
                "🔄 Refreshing menu .",
                "🔄 Refreshing menu . .",
                "🔄 Refreshing menu . . .",
                "✨ Menu refreshed!"
            ]
            
            # Show loading animation
            for i, loading_text in enumerate(loading_states[:-1]):
                await query.edit_message_text(loading_text)
                await asyncio.sleep(0.3)  # Short pause for animation effect
            
            # Show final success state briefly
            await query.edit_message_text(loading_states[-1])
            await asyncio.sleep(0.5)
            
            # Refresh the main menu with updated content
            keyboard = [
                [
                    InlineKeyboardButton("💰 Bitcoin Price", callback_data="quick_price_bitcoin"),
                    InlineKeyboardButton("📈 Ethereum Price", callback_data="quick_price_ethereum"),
                ],
                [
                    InlineKeyboardButton("🔥 Trending Coins", callback_data="quick_trending"),
                    InlineKeyboardButton("📊 My Portfolio", callback_data="quick_portfolio"),
                ],
                [
                    InlineKeyboardButton("🤖 AI Analysis", callback_data="quick_ai_menu"),
                    InlineKeyboardButton("🔔 My Alerts", callback_data="quick_alerts"),
                ],
                [
                    InlineKeyboardButton("🎮 Crypto Quiz", callback_data="quick_quiz"),
                    InlineKeyboardButton("📱 More Commands", callback_data="quick_help"),
                ],
                [
                    InlineKeyboardButton("🔄 Refresh Menu", callback_data="quick_refresh"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Get current timestamp for freshness indicator
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M")
            
            await query.edit_message_text(
                f"⚡ **Quick Actions Menu**\n\n"
                f"Choose an action below for instant results:\n\n"
                f"🕐 Last updated: {current_time}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        elif query.data == "quick_price_bitcoin":
            await query.edit_message_text("🔍 Fetching Bitcoin price...")
            price_data = await price_service.get_price("bitcoin")
            if price_data:
                message = format_price_message("bitcoin", "bitcoin", price_data)
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Unable to fetch Bitcoin price. Please try again.")
                
        elif query.data == "quick_price_ethereum":
            await query.edit_message_text("🔍 Fetching Ethereum price...")
            price_data = await price_service.get_price("ethereum")
            if price_data:
                message = format_price_message("ethereum", "ethereum", price_data)
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Unable to fetch Ethereum price. Please try again.")
                
        elif query.data == "quick_trending":
            await query.edit_message_text("🔍 Fetching trending cryptocurrencies...")
            trending_data = await market_service.get_trending_coins()
            if trending_data:
                message = "🔥 **Trending Cryptocurrencies**\n\n"
                for i, coin in enumerate(trending_data[:7], 1):
                    name = coin.get('name', 'Unknown')
                    symbol = coin.get('symbol', '').upper()
                    market_cap_rank = coin.get('market_cap_rank', 'N/A')
                    message += f"{i}. **{name}** ({symbol}) - Rank #{market_cap_rank}\n"
                message += "\n💡 Use /shouldibuy [COIN] for AI analysis"
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Unable to fetch trending data. Please try again.")
                
        elif query.data == "quick_portfolio":
            user_id = str(query.from_user.id)
            default_wallet = await wallet_service.get_default_wallet(user_id)
            
            if default_wallet:
                await query.edit_message_text("🔍 Fetching your portfolio...")
                portfolio_data = await portfolio_service.get_wallet_portfolio(
                    default_wallet['address'], 
                    default_wallet['blockchain']
                )
                if portfolio_data:
                    message = format_portfolio_message(portfolio_data)
                    await query.edit_message_text(message, parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ Unable to fetch portfolio data. Please try again.")
            else:
                await query.edit_message_text(
                    "❌ No default wallet set!\n\n"
                    "Use /setwallet [WALLET_ADDRESS] to save your default wallet first."
                )
                
        elif query.data == "quick_alerts":
            user_id = str(query.from_user.id)
            alerts = await alert_service.get_user_alerts(user_id)
            
            if alerts:
                message = "🔔 **Your Active Alerts**\n\n"
                for i, alert in enumerate(alerts[:5], 1):
                    symbol = alert['coin_symbol'].upper()
                    target = alert['target_price']
                    direction = "above" if alert['is_above'] else "below"
                    message += f"{i}. {symbol}: Alert when {direction} ${target:,.2f}\n"
                
                if len(alerts) > 5:
                    message += f"\n... and {len(alerts) - 5} more alerts"
                    
                message += "\n\n💡 Use /setalert [COIN] [PRICE] to add more"
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text(
                    "🔔 **No Active Alerts**\n\n"
                    "Use /setalert [COIN] [PRICE] to create your first price alert!"
                )
                
        elif query.data == "quick_ai_menu":
            await quick_ai_menu(update, context)
            
        elif query.data == "quick_quiz":
            # Start a beginner quiz directly from quick menu
            user_id = str(query.from_user.id)
            
            # Check if user has an active quiz session
            if quiz_service.has_active_session(user_id):
                current_question = quiz_service.get_current_question(user_id)
                if current_question and "error" not in current_question:
                    await send_next_quiz_question(query, current_question)
                    return
                else:
                    quiz_service.end_session(user_id)
            
            # Start new beginner quiz
            question_data = quiz_service.start_quiz(user_id, "beginner")
            if question_data and "error" not in question_data:
                await send_next_quiz_question(query, question_data)
            else:
                await query.edit_message_text(
                    "❌ Sorry, I couldn't start the quiz. Try /quiz command instead."
                )
            
        elif query.data == "start_menu":
            # Create Quick Actions menu for callback query
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            from datetime import datetime
            
            keyboard = [
                [
                    InlineKeyboardButton("💰 Quick Price Check", callback_data="quick_price"),
                    InlineKeyboardButton("🤖 AI Analysis", callback_data="quick_ai_menu"),
                ],
                [
                    InlineKeyboardButton("📈 Trending Coins", callback_data="quick_trending"),
                    InlineKeyboardButton("💼 Portfolio", callback_data="quick_portfolio"),
                ],
                [
                    InlineKeyboardButton("🔔 Your Alerts", callback_data="quick_alerts"),
                    InlineKeyboardButton("🎮 Crypto Quiz", callback_data="quick_quiz"),
                ],
                [
                    InlineKeyboardButton("🔄 Refresh Menu", callback_data="quick_refresh"),
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            current_time = datetime.now().strftime("%H:%M:%S")
            
            await query.edit_message_text(
                f"⚡ **Quick Actions Menu**\n\n"
                f"Choose an action below for instant results:\n\n"
                f"🕒 Updated: {current_time}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        elif query.data == "quick_ai_bitcoin":
            await query.edit_message_text("🤖 Analyzing Bitcoin for you...")
            coin_data = await market_service.get_detailed_coin_data("bitcoin")
            if coin_data:
                analysis = await ai_analyst.should_i_buy_analysis(coin_data)
                message = f"🤖 **Bitcoin Analysis**\n\n{analysis}"
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Unable to fetch Bitcoin data for analysis.")
                
        elif query.data == "quick_ai_ethereum":
            await query.edit_message_text("🤖 Analyzing Ethereum for you...")
            coin_data = await market_service.get_detailed_coin_data("ethereum")
            if coin_data:
                analysis = await ai_analyst.should_i_buy_analysis(coin_data)
                message = f"🤖 **Ethereum Analysis**\n\n{analysis}"
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Unable to fetch Ethereum data for analysis.")
                
        elif query.data == "quick_daily":
            await query.edit_message_text("🤖 Generating daily market summary...")
            top_coins = await market_service.get_top_coins_by_market_cap(10)
            if top_coins:
                summary = await ai_analyst.generate_daily_summary(top_coins)
                message = f"📊 **Daily Market Summary**\n\n{summary}"
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Unable to generate market summary.")
                
        elif query.data == "quick_custom_ai":
            await query.edit_message_text(
                "🔍 **Custom AI Analysis**\n\n"
                "Use: /shouldibuy [COIN_NAME]\n\n"
                "Examples:\n"
                "• /shouldibuy bitcoin\n"
                "• /shouldibuy solana\n"
                "• /shouldibuy cardano\n\n"
                "💡 I'll analyze any of 220+ supported coins!"
            )
            
        elif query.data == "quick_help":
            await query.edit_message_text(
                "📱 **All Available Commands**\n\n"
                "🚀 **AI Commands:**\n"
                "• /shouldibuy [COIN] - AI trading advice\n"
                "• /trending - Trending cryptocurrencies\n"
                "• /daily - AI market summary\n\n"
                "📊 **Data Commands:**\n"
                "• /price [COIN] - Live prices\n"
                "• /allcoins - Supported coins\n\n"
                "🔔 **Alerts & Portfolio:**\n"
                "• /setalert [COIN] [PRICE] - Set alerts\n"
                "• /alerts - View your alerts\n"
                "• /portfolio [WALLET] - Check holdings\n"
                "• /setwallet [WALLET] - Save default wallet\n\n"
                "🎮 **Educational:**\n"
                "• /quiz [difficulty] - Crypto quiz game\n"
                "• /quizstats - Your quiz statistics\n\n"
                "⚡ **Quick Actions:**\n"
                "• /menu - Open this quick menu\n\n"
                "Type /help for detailed instructions."
            )
            
        # Currency converter callback handling
        elif query.data.startswith("convert_"):
            try:
                parts = query.data.split("_", 3)
                if len(parts) == 4:
                    amount = float(parts[1])
                    from_currency = parts[2].upper()
                    to_currency = parts[3].upper()
                    
                    await query.edit_message_text("💱 Converting currencies...")
                    
                    # Perform conversion
                    conversion = await currency_converter.convert_currency(amount, from_currency, to_currency)
                    
                    if conversion and 'error' not in conversion:
                        result_text = currency_converter.format_conversion_result(conversion)
                        if conversion.get('timestamp'):
                            result_text += f"\n🕐 Updated: {conversion['timestamp']}"
                        
                        await query.edit_message_text(result_text)
                    else:
                        error_msg = conversion.get('error', 'Conversion failed') if conversion else 'Unable to fetch rates'
                        await query.edit_message_text(f"❌ {error_msg}")
                
            except Exception as e:
                logger.error(f"Error in convert callback: {e}")
                await query.edit_message_text("❌ Conversion failed")
        
        # Swap-related callbacks
        elif query.data.startswith("swap_"):
            await query.answer()
            
            if query.data == "swap_cancel":
                await query.edit_message_text("❌ **Swap Cancelled**\n\nYou can try again anytime with `/swap`")
            
            elif query.data == "swap_supported_chains":
                chains_message = rango_swap_service.get_supported_chains_list()
                keyboard = [
                    [InlineKeyboardButton("💰 View Tokens", callback_data="swap_supported_tokens")],
                    [InlineKeyboardButton("📚 Examples", callback_data="swap_examples")],
                    [InlineKeyboardButton("🔙 Back", callback_data="swap_back_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(chains_message, parse_mode='Markdown', reply_markup=reply_markup)
            
            elif query.data == "swap_supported_tokens":
                tokens_message = rango_swap_service.get_popular_tokens_list()
                keyboard = [
                    [InlineKeyboardButton("🔗 View Chains", callback_data="swap_supported_chains")],
                    [InlineKeyboardButton("📚 Examples", callback_data="swap_examples")],
                    [InlineKeyboardButton("🔙 Back", callback_data="swap_back_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(tokens_message, parse_mode='Markdown', reply_markup=reply_markup)
            
            elif query.data == "swap_examples":
                examples_message = """🔁 **Swap Examples**

**Popular Cross-Chain Swaps:**

🔸 **Ethereum to BNB Chain:**
`/swap ETH BNB 0.1`

🔸 **Bitcoin to Stablecoins:**
`/swap BTC USDC 0.001`
`/swap BTC USDT 0.005`

🔸 **Solana to Ethereum:**
`/swap SOL ETH 5.0`

🔸 **Layer 2 to Layer 1:**
`/swap MATIC ETH 100`

🔸 **TRON to other chains:**
`/swap TRX BNB 1000`
`/swap TRX ETH 500`

**Commands:**
• `/swap` - Execute swap with confirmation
• `/swapquote` - Get price quote only
• `/swapsupported` - View all supported assets

💡 **Tip:** Always check quotes first with `/swapquote` before executing swaps!"""

                keyboard = [
                    [InlineKeyboardButton("🔗 Chains", callback_data="swap_supported_chains")],
                    [InlineKeyboardButton("💰 Tokens", callback_data="swap_supported_tokens")],
                    [InlineKeyboardButton("🔙 Back", callback_data="swap_back_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(examples_message, parse_mode='Markdown', reply_markup=reply_markup)
            
            elif query.data == "swap_back_main":
                message = """🔁 **Rango Exchange Integration**

Cross-chain swaps powered by Rango Exchange, supporting 20+ blockchains and 1000+ tokens.

**Quick Examples:**
• `/swap ETH BNB 0.1` - Swap ETH to BNB
• `/swap BTC USDC 0.001` - Swap BTC to USDC  
• `/swap SOL MATIC 5.0` - Swap SOL to MATIC

**Available Commands:**
• `/swap` - Execute cross-chain swap
• `/swapquote` - Get price quote only
• `/swapsupported` - View supported assets

Use the buttons below to explore supported chains and tokens."""
                
                keyboard = [
                    [
                        InlineKeyboardButton("🔗 Chains", callback_data="swap_supported_chains"),
                        InlineKeyboardButton("💰 Tokens", callback_data="swap_supported_tokens")
                    ],
                    [InlineKeyboardButton("📚 Examples", callback_data="swap_examples")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
            elif query.data.startswith("swap_confirm_"):
                # Handle swap confirmation
                parts = query.data.split("_")
                if len(parts) >= 5:
                    from_token = parts[2]
                    to_token = parts[3]
                    amount = parts[4]
                    
                    # For now, show that swap would be initiated (actual implementation would require wallet integration)
                    confirmation_message = f"""✅ **Swap Confirmation**

🔁 **Trade:** {amount} {from_token} ➝ {to_token}

⚠️ **Important Notice:**
To complete cross-chain swaps, you'll need to:

1. Connect your wallet externally
2. Sign the transaction with your private key
3. Monitor swap progress on Rango Exchange

🔄 **Next Steps:**
• Visit Rango Exchange directly for wallet integration
• Use their dApp for secure transaction signing
• Track your swap progress via transaction hash

💡 This bot provides quotes and guidance, but actual swaps require external wallet connection for security."""
                    
                    await query.edit_message_text(confirmation_message, parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ Invalid swap confirmation data.")
        
        # Chart type switching callback handling
        elif query.data.startswith("chart_"):
            try:
                # Parse chart callback data: chart_coin_id_days_type
                parts = query.data.split("_")
                if len(parts) >= 4:
                    coin_id = parts[1]
                    days = int(parts[2])
                    chart_type = parts[3]
                    
                    # Get coin symbol from mapper
                    coin_symbol = None
                    for symbol, mapped_id in coin_mapper.coin_mapping.items():
                        if mapped_id == coin_id:
                            coin_symbol = symbol.upper()
                            break
                    
                    if not coin_symbol:
                        coin_symbol = coin_id.upper()
                    
                    await query.edit_message_text("📈 Generating new chart...")
                    
                    # Generate new chart with different type
                    chart_bytes = await chart_service.generate_price_chart(coin_id, coin_symbol, days, chart_type)
                    
                    if chart_bytes:
                        from io import BytesIO
                        chart_file = BytesIO(chart_bytes)
                        chart_file.name = f"{coin_symbol}_{days}d_{chart_type}.png"
                        
                        # Chart type display names
                        chart_type_names = {
                            'line': 'Line',
                            'area': 'Area', 
                            'candlestick': 'Technical Analysis',
                            'volume': 'Price & Volume'
                        }
                        
                        # Chart descriptions
                        chart_info = {
                            'line': '📊 Clean price line chart',
                            'area': '🔵 Filled area chart',
                            'candlestick': '📈 Technical analysis with moving averages',
                            'volume': '📊 Price chart with trading volume'
                        }
                        
                        # Create updated keyboard
                        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                        keyboard = [
                            [
                                InlineKeyboardButton("📊 Line", callback_data=f"chart_{coin_id}_{days}_line"),
                                InlineKeyboardButton("🔵 Area", callback_data=f"chart_{coin_id}_{days}_area"),
                            ],
                            [
                                InlineKeyboardButton("📈 Technical", callback_data=f"chart_{coin_id}_{days}_candlestick"),
                                InlineKeyboardButton("📊 Volume", callback_data=f"chart_{coin_id}_{days}_volume"),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        # Send updated chart
                        await query.message.reply_photo(
                            photo=chart_file,
                            caption=f"📈 **{coin_symbol} {chart_type_names[chart_type]} Chart ({days} Days)**\n\n"
                                   f"{chart_info[chart_type]}\n"
                                   f"Generated with live market data from CoinGecko\n\n"
                                   f"💡 *Try different chart types using the buttons below*",
                            parse_mode='Markdown',
                            reply_markup=reply_markup
                        )
                        
                        # Delete the loading message
                        await query.delete_message()
                    else:
                        await query.edit_message_text("❌ Failed to generate chart")
                        
            except Exception as e:
                logger.error(f"Error in chart callback: {e}")
                await query.edit_message_text("❌ Chart generation failed")
        
        # Quiz callback handling
        elif query.data == "quiz_quit":
            user_id = str(query.from_user.id)
            quiz_service.end_session(user_id)
            await query.edit_message_text("❌ Quiz ended. Thanks for playing! Start a new quiz anytime with /quiz.")
            
        elif query.data.startswith("quiz_answer_"):
            user_id = str(query.from_user.id)
            answer_index = int(query.data.split("_")[-1])
            result = quiz_service.submit_answer(user_id, answer_index)
            
            if "error" in result:
                await query.edit_message_text("❌ Quiz session expired. Start a new quiz with /quiz.")
                return
            
            # Show result
            result_emoji = "✅" if result['is_correct'] else "❌"
            result_text = f"""{result_emoji} **{'Correct!' if result['is_correct'] else 'Incorrect!'}**

💡 **Explanation:** {result['explanation']}

📊 **Score:** {result['score']}/{result['total_questions']}"""
            
            await query.edit_message_text(result_text, parse_mode='Markdown')
            
            # Check if quiz is completed
            if result.get('quiz_completed'):
                final_results = result['final_results']
                final_message = f"""🎉 **Quiz Completed!**

{final_results['performance']} {final_results['message']}

📊 **Final Results:**
• Score: {final_results['score']}/{final_results['total_questions']} ({final_results['percentage']:.1f}%)
• Difficulty: {final_results['difficulty'].title()}
• Duration: {final_results['duration']} seconds

🎮 Start another quiz: /quiz [beginner/intermediate/advanced]"""
                
                await query.message.reply_text(
                    text=final_message,
                    parse_mode='Markdown'
                )
            else:
                # Send next question after a short delay
                await asyncio.sleep(2)
                next_question = quiz_service.get_current_question(user_id)
                if next_question and "error" not in next_question:
                    await send_next_quiz_question(query, next_question)
            
    except Exception as e:
        logger.error(f"Error in callback query handler: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")

async def send_next_quiz_question(query, question_data: Dict) -> None:
    """Send next quiz question via callback query."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    question_text = f"""🎮 **Crypto Quiz - {question_data['difficulty'].title()} Level**

📝 **Question {question_data['question_number']}/{question_data['total_questions']}**

{question_data['question']}

Choose your answer:"""
    
    # Create inline keyboard with answer options
    keyboard = []
    for i, option in enumerate(question_data['options']):
        keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option}", callback_data=f"quiz_answer_{i}")])
    
    # Add quit option
    keyboard.append([InlineKeyboardButton("❌ Quit Quiz", callback_data="quiz_quit")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=question_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def setup_bot_commands(bot) -> None:
    """Set up persistent bot command menu using setMyCommands API."""
    from telegram import BotCommand
    
    commands = [
        BotCommand("start", "Start the bot and see welcome message"),
        BotCommand("price", "Get live cryptocurrency prices"),
        BotCommand("chart", "Generate price history charts"),
        BotCommand("shouldibuy", "Get AI-powered trading advice"),
        BotCommand("trending", "View trending cryptocurrencies"),
        BotCommand("daily", "Get AI market summary"),
        BotCommand("portfolio", "Check wallet holdings"),
        BotCommand("createwallet", "Generate new multi-chain wallet"),
        BotCommand("mywallet", "View your wallet addresses and balances"),
        BotCommand("receive", "Get addresses for receiving crypto"),
        BotCommand("setalert", "Set price alerts"),
        BotCommand("alerts", "View your active alerts"),
        BotCommand("startlive", "Start live price notifications"),
        BotCommand("stoplive", "Stop live price notifications"),
        BotCommand("mylive", "View active live notifications"),
        BotCommand("setcurrency", "Set preferred currencies for prices"),
        BotCommand("scan", "Multi-chain token analysis with AI risk assessment"),
        BotCommand("swap", "Execute cross-chain cryptocurrency swaps"),
        BotCommand("swapquote", "Get cross-chain swap price quotes"),
        BotCommand("swapsupported", "View supported chains and tokens for swaps"),
        BotCommand("quiz", "Take crypto education quiz"),
        BotCommand("menu", "Quick actions menu"),
        BotCommand("help", "Complete guide to all commands")
    ]
    
    try:
        await bot.set_my_commands(commands)
        logger.info("Bot commands menu set successfully")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")

async def send_alert_notification(application: Application, user_id: str, alert_info: dict) -> None:
    """Send alert notification to user."""
    try:
        symbol = alert_info['coin_symbol'].upper()
        current_price = alert_info['current_price']
        target_price = alert_info['target_price']
        direction = "above" if alert_info['is_above'] else "below"
        
        message = (
            f"🚨 **PRICE ALERT TRIGGERED!** 🚨\n\n"
            f"📈 **{symbol}** has reached your target!\n\n"
            f"💰 Current Price: **${current_price:,.2f}**\n"
            f"🎯 Target Price: **${target_price:,.2f}** ({direction})\n\n"
            f"⏰ Alert triggered at {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"💡 Use /shouldibuy {symbol.lower()} for AI analysis"
        )
        
        await application.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Alert notification sent to user {user_id} for {symbol}")
        
    except Exception as e:
        logger.error(f"Failed to send alert notification to user {user_id}: {e}")

async def price_monitoring_task(application: Application) -> None:
    """Background task to monitor price alerts."""
    logger.info("Starting price monitoring task...")
    
    while True:
        try:
            # Check for triggered alerts
            triggered_alerts = await alert_service.check_alerts_and_notify()
            
            if triggered_alerts:
                logger.info(f"Found {len(triggered_alerts)} triggered alerts")
                
                # Send notifications to users
                for alert in triggered_alerts:
                    await send_alert_notification(application, alert['user_id'], alert)
                    # Small delay between notifications
                    await asyncio.sleep(1)
            
            # Wait 60 seconds before next check
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in price monitoring task: {e}")
            # Wait 60 seconds before retrying on error
            await asyncio.sleep(60)

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /send command for sending funds"""
    try:
        user_id = str(update.effective_user.id)
        
        # Check if user has a wallet
        wallet_data = await multi_wallet_service.get_wallet(user_id)
        if not wallet_data:
            await update.message.reply_text(
                "❌ No wallet found!\n\n"
                "Create a wallet first using /wallet command."
            )
            return
        
        # Check if user provided arguments
        if not context.args or len(context.args) < 3:
            # Get wallet balances to show available funds
            balances = await multi_wallet_service.get_wallet_balances(user_id)
            if not balances:
                await update.message.reply_text(
                    "❌ Unable to fetch wallet balances.\n"
                    "Please try again later."
                )
                return
            
            # Show available balances for sending
            balance_text = "💸 **Send Cryptocurrency**\n\n"
            balance_text += "Available balances:\n"
            
            available_chains = []
            for chain, balance_info in balances.items():
                # Extract numeric balance from dictionary structure
                if isinstance(balance_info, dict) and "balance" in balance_info:
                    try:
                        balance_value = float(balance_info["balance"])
                        symbol = balance_info.get("symbol", chain.upper())
                    except (ValueError, TypeError):
                        balance_value = 0.0
                        symbol = chain.upper()
                else:
                    balance_value = float(balance_info) if balance_info else 0.0
                    symbol = {
                        'ethereum': 'ETH',
                        'bsc': 'BNB', 
                        'polygon': 'MATIC',
                        'solana': 'SOL',
                        'tron': 'TRX'
                    }.get(chain, chain.upper())
                
                if balance_value > 0:
                    balance_text += f"• {symbol}: {balance_value:.6f}\n"
                    available_chains.append(chain)
            
            if not available_chains:
                await update.message.reply_text(
                    "❌ No funds available to send.\n\n"
                    "Your wallet has zero balance on all networks."
                )
                return
            
            balance_text += "\n📝 **To send funds, use:**\n"
            balance_text += "`/send <chain> <amount> <address>`\n\n"
            balance_text += "**Examples:**\n"
            balance_text += "• `/send tron 1.5 TQn9Y2khEsLMG73Lkkpj...`\n"
            balance_text += "• `/send ethereum 0.01 0x742d35Cc6ab..`\n"
            balance_text += "• `/send bsc 0.1 0x742d35Cc6ab..`\n\n"
            balance_text += "**Supported chains:**\n"
            balance_text += "• `tron` (TRX)\n"
            balance_text += "• `ethereum` (ETH)\n"
            balance_text += "• `bsc` (BNB)\n"
            balance_text += "• `polygon` (MATIC)\n"
            balance_text += "• `solana` (SOL)"
            
            await update.message.reply_text(balance_text, parse_mode='Markdown')
            return
        
        # Parse arguments
        chain = context.args[0].lower()
        try:
            amount = float(context.args[1])
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid amount! Please enter a valid number.\n"
                "Example: `/send tron 1.5 TQn9Y2khEsLMG73Lkkpj...`"
            )
            return
        
        to_address = context.args[2]
        
        # Validate chain
        supported_chains = ['ethereum', 'bsc', 'polygon', 'solana', 'tron']
        if chain not in supported_chains:
            await update.message.reply_text(
                f"❌ Unsupported chain: {chain}\n\n"
                f"Supported chains: {', '.join(supported_chains)}"
            )
            return
        
        # Validate amount
        if amount <= 0:
            await update.message.reply_text(
                "❌ Amount must be greater than 0!"
            )
            return
        
        # Check balance
        balances = await multi_wallet_service.get_wallet_balances(user_id)
        if not balances or chain not in balances:
            await update.message.reply_text(
                f"❌ Unable to fetch {chain} balance.\n"
                f"Please try again later."
            )
            return
        
        # Extract numeric balance from the balance dictionary
        balance_data = balances[chain]
        if isinstance(balance_data, dict) and "balance" in balance_data:
            try:
                current_balance = float(balance_data["balance"])
            except (ValueError, TypeError):
                current_balance = 0.0
        else:
            current_balance = float(balance_data) if balance_data else 0.0
        if current_balance < amount:
            available_balance = current_balance
            symbol = {
                'ethereum': 'ETH',
                'bsc': 'BNB',
                'polygon': 'MATIC', 
                'solana': 'SOL',
                'tron': 'TRX'
            }.get(chain, chain.upper())
            
            await update.message.reply_text(
                f"❌ Insufficient balance!\n\n"
                f"Available {symbol}: {available_balance:.6f}\n"
                f"Requested: {amount:.6f}"
            )
            return
        
        # Show confirmation
        symbol = {
            'ethereum': 'ETH',
            'bsc': 'BNB',
            'polygon': 'MATIC',
            'solana': 'SOL', 
            'tron': 'TRX'
        }.get(chain, chain.upper())
        
        await update.message.reply_text(
            f"⏳ Sending {amount} {symbol} on {chain.title()} network...\n"
            f"To: `{to_address}`\n\n"
            f"Please wait while the transaction is processed..."
        )
        
        # Send transaction
        result = await multi_wallet_service.send_transaction(user_id, chain, to_address, amount)
        
        if result["success"]:
            await update.message.reply_text(
                f"✅ **Transaction Successful!**\n\n"
                f"💰 Amount: {amount} {symbol}\n"
                f"🔗 Chain: {chain.title()}\n"
                f"📤 From: `{result['from']}`\n"
                f"📥 To: `{result['to']}`\n"
                f"🔗 TX Hash: `{result['tx_hash']}`\n\n"
                f"Your transaction has been broadcast to the blockchain!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ **Transaction Failed!**\n\n"
                f"Error: {result['error']}\n\n"
                f"Please check the recipient address and try again."
            )
        
    except Exception as e:
        logger.error(f"Error in send command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while processing your transaction.\n"
            "Please try again later."
        )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "❓ Unknown command!\n\n"
        "🚀 AI Commands:\n"
        "• /shouldibuy [COIN] - AI trading advice\n"
        "• /trending - Trending cryptocurrencies\n"
        "• /daily - AI market summary\n\n"
        "📊 Data Commands:\n"
        "• /price [COIN] - Live prices\n"
        "• /allcoins - Supported coins\n\n"
        "🔔 Alerts & Portfolio:\n"
        "• /setalert [COIN] [PRICE] - Set alerts\n"
        "• /alerts - View your alerts\n"
        "• /portfolio [WALLET] - Check holdings\n"
        "• /setwallet [WALLET] - Save default wallet\n\n"
        "Type /help for detailed instructions."
    )

def main() -> None:
    """Start the bot."""
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("allcoins", allcoins_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("chart", chart_command))
    
    # AI-powered commands
    application.add_handler(CommandHandler("shouldibuy", shouldibuy_command))
    application.add_handler(CommandHandler("trending", trending_command))
    application.add_handler(CommandHandler("daily", daily_command))
    
    # Alert commands
    application.add_handler(CommandHandler("setalert", setalert_command))
    application.add_handler(CommandHandler("alerts", alerts_command))
    application.add_handler(CommandHandler("deletealert", delete_alert_command))
    
    # Live notification commands
    application.add_handler(CommandHandler("startlive", start_live_command))
    application.add_handler(CommandHandler("stoplive", stop_live_command))
    application.add_handler(CommandHandler("mylive", my_live_command))
    application.add_handler(CommandHandler("swap", swap_command))
    application.add_handler(CommandHandler("swapquote", swapquote_command))
    application.add_handler(CommandHandler("swapsupported", swapsupported_command))
    
    # Portfolio commands
    application.add_handler(CommandHandler("portfolio", portfolio_command))
    application.add_handler(CommandHandler("setcurrency", setcurrency_command))
    application.add_handler(CommandHandler("convert", convert_command))
    application.add_handler(CommandHandler("totalusers", totalusers_command))
    application.add_handler(CommandHandler("setwallet", setwallet_command))
    application.add_handler(CommandHandler("send", send_command))
    
    # Quick Actions menu
    application.add_handler(CommandHandler("menu", menu_command))
    
    # Multi-chain wallet commands
    application.add_handler(CommandHandler("createwallet", createwallet_command))
    application.add_handler(CommandHandler("mywallet", mywallet_command))
    application.add_handler(CommandHandler("receive", receive_command))
    
    # Quiz commands
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("quizstats", quizstats_command))
    application.add_handler(CommandHandler("scan", scan_command))
    
    # Personalized recommendation commands
    application.add_handler(CommandHandler("recommend", recommend_command))
    application.add_handler(CommandHandler("insights", insights_command))
    application.add_handler(CommandHandler("riskprofile", riskprofile_command))
    
    # Register callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Log bot startup
    logger.info("Starting AI Crypto Assistant Bot...")
    
    # Start the price monitoring task
    async def post_init(application: Application) -> None:
        """Initialize background tasks after bot starts."""
        # Set up bot commands menu
        await setup_bot_commands(application.bot)
        
        logger.info("Starting background price monitoring...")
        asyncio.create_task(price_monitoring_task(application))
    
    application.post_init = post_init
    
    # Check if running in deployment mode
    import os
    port = int(os.environ.get('PORT', 5000))
    
    # Force webhook mode when port is explicitly set (deployment mode)
    if os.environ.get('PORT') or os.environ.get('REPLIT_DEPLOYMENT'):
        # Production mode with webhooks
        logger.info(f"Starting bot in webhook mode on port {port}")
        try:
            # Get webhook URL from environment or construct it
            webhook_url = os.environ.get('WEBHOOK_URL')
            if not webhook_url:
                repl_slug = os.environ.get('REPL_SLUG', 'crypto-bot')
                replit_domain = os.environ.get('REPLIT_DOMAINS', 'replit.app')
                webhook_url = f"https://{repl_slug}.{replit_domain}/webhook"
            
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path="/webhook",
                webhook_url=webhook_url
            )
        except Exception as e:
            logger.error(f"Webhook mode failed: {e}")
    else:
        # Development mode with polling
        logger.info("Bot is now running in polling mode. Press Ctrl+C to stop.")
        try:
            import asyncio
            import threading
            import signal
            
            # Disable signal handling in threads
            if threading.current_thread() is not threading.main_thread():
                signal.signal = lambda signum, handler: None
            
            # Use run_polling with proper async handling
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(application.run_polling(allowed_updates=Update.ALL_TYPES))
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            # Try alternative polling method for threaded environments
            try:
                logger.info("Attempting alternative polling method...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def start_polling():
                    await application.initialize()
                    await application.start()
                    # Start background monitoring task
                    await setup_bot_commands(application.bot)
                    logger.info("Starting background price monitoring...")
                    asyncio.create_task(price_monitoring_task(application))
                    await application.updater.start_polling()
                    # Keep running
                    while True:
                        await asyncio.sleep(1)
                
                loop.run_until_complete(start_polling())
            except Exception as e2:
                logger.error(f"Alternative polling also failed: {e2}")

async def start_live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start live price notifications for a cryptocurrency"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a cryptocurrency to monitor.\n\n"
            "Usage: `/startlive bitcoin`\n"
            "Example: `/startlive ethereum`\n\n"
            "You'll receive price updates every minute!",
            parse_mode='Markdown'
        )
        return
    
    user_id = str(update.effective_user.id)
    coin_symbol = context.args[0].lower()
    
    try:
        await track_user_safely(update.effective_user)
        
        result = await live_notification_service.add_live_notification(user_id, coin_symbol)
        
        if result["success"]:
            await update.message.reply_text(
                f"📡 **Live notifications started!**\n\n"
                f"You'll now receive **{result['coin_symbol']}** price updates every minute.\n\n"
                f"💡 Use `/stoplive {coin_symbol}` to stop notifications\n"
                f"📋 Use `/mylive` to see all active notifications",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"❌ {result['error']}")
            
    except Exception as e:
        logger.error(f"Error starting live notification: {e}")
        await update.message.reply_text("❌ Failed to start live notifications. Please try again.")

async def stop_live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop live price notifications"""
    user_id = str(update.effective_user.id)
    
    try:
        await track_user_safely(update.effective_user)
        
        if context.args:
            # Stop specific coin notification
            coin_symbol = context.args[0].lower()
            result = await live_notification_service.remove_live_notification(user_id, coin_symbol)
            
            if result["success"]:
                await update.message.reply_text(
                    f"⏹️ **Live notifications stopped!**\n\n"
                    f"Stopped **{result['coin_symbol']}** price updates.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(f"❌ {result['error']}")
        else:
            # Stop all notifications
            result = await live_notification_service.remove_live_notification(user_id)
            
            if result["success"]:
                await update.message.reply_text(
                    f"⏹️ **All live notifications stopped!**\n\n"
                    f"Stopped {result['count']} active notifications.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(f"❌ {result['error']}")
                
    except Exception as e:
        logger.error(f"Error stopping live notification: {e}")
        await update.message.reply_text("❌ Failed to stop live notifications. Please try again.")

async def my_live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's active live notifications"""
    user_id = str(update.effective_user.id)
    
    try:
        await track_user_safely(update.effective_user)
        
        notifications = await live_notification_service.get_user_notifications(user_id)
        
        if not notifications:
            await update.message.reply_text(
                "📡 **No Active Live Notifications**\n\n"
                "You don't have any live price notifications running.\n\n"
                "💡 Use `/startlive bitcoin` to start getting live price updates!"
            )
            return
        
        message = "📡 **Your Live Notifications**\n\n"
        
        for notif in notifications:
            created_time = notif["created_at"].strftime("%Y-%m-%d %H:%M")
            last_sent_text = "Never" if not notif["last_sent"] else notif["last_sent"].strftime("%H:%M")
            
            message += (
                f"🔸 **{notif['coin_symbol']}**\n"
                f"   📅 Started: {created_time}\n"
                f"   🕐 Last sent: {last_sent_text}\n\n"
            )
        
        message += f"📊 Total: {len(notifications)} active notification(s)\n\n"
        message += "💡 Use `/stoplive <coin>` to stop specific notifications\n"
        message += "💡 Use `/stoplive` to stop all notifications"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting live notifications: {e}")
        await update.message.reply_text("❌ Failed to get live notifications. Please try again.")

async def swap_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /swap command for cross-chain swaps"""
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "🔁 **Cross-Chain Swap**\n\n"
            "Usage: `/swap [from_token] [to_token] [amount]`\n\n"
            "Examples:\n"
            "• `/swap ETH BNB 0.1`\n"
            "• `/swap BTC USDC 0.001`\n"
            "• `/swap SOL ETH 1.5`\n\n"
            "💡 Use `/swapsupported` to see all supported tokens",
            parse_mode='Markdown'
        )
        return
    
    user_id = str(update.effective_user.id)
    
    try:
        await track_user_safely(update.effective_user)
        
        from_token = context.args[0].upper()
        to_token = context.args[1].upper()
        amount = context.args[2]
        
        # Validate amount
        try:
            float(amount)
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a valid number.")
            return
        
        # Send loading message
        loading_msg = await update.message.reply_text(
            f"🔍 Getting swap quote for {amount} {from_token} ➝ {to_token}...",
            parse_mode='Markdown'
        )
        
        # Get swap quote
        quote_data = await rango_swap_service.get_swap_quote(
            from_token=from_token,
            to_token=to_token,
            amount=amount
        )
        
        if not quote_data:
            await loading_msg.edit_text(
                f"❌ **Swap Quote Failed**\n\n"
                f"Could not get quote for {from_token} ➝ {to_token}\n\n"
                f"Possible reasons:\n"
                f"• Token not supported\n"
                f"• Invalid amount\n"
                f"• No route available\n\n"
                f"💡 Use `/swapsupported` to check supported tokens",
                parse_mode='Markdown'
            )
            return
        
        # Format and display quote
        quote_message = rango_swap_service.format_swap_quote(quote_data)
        
        # Create inline keyboard for swap actions
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm Swap", callback_data=f"swap_confirm_{from_token}_{to_token}_{amount}"),
                InlineKeyboardButton("❌ Cancel", callback_data="swap_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await loading_msg.edit_text(
            quote_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in swap command: {e}")
        await update.message.reply_text("❌ Failed to get swap quote. Please try again.")

async def swapquote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /swapquote command for getting swap quotes"""
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "💰 **Swap Quote**\n\n"
            "Usage: `/swapquote [from_token] [to_token] [amount]`\n\n"
            "Examples:\n"
            "• `/swapquote ETH USDC 1.0`\n"
            "• `/swapquote BTC SOL 0.5`\n"
            "• `/swapquote MATIC BNB 100`\n\n"
            "💡 This shows pricing without executing the swap",
            parse_mode='Markdown'
        )
        return
    
    user_id = str(update.effective_user.id)
    
    try:
        await track_user_safely(update.effective_user)
        
        from_token = context.args[0].upper()
        to_token = context.args[1].upper()
        amount = context.args[2]
        
        # Validate amount
        try:
            float(amount)
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a valid number.")
            return
        
        # Send loading message
        loading_msg = await update.message.reply_text(
            f"📊 Calculating quote for {amount} {from_token} ➝ {to_token}...",
            parse_mode='Markdown'
        )
        
        # Get swap quote
        quote_data = await rango_swap_service.get_swap_quote(
            from_token=from_token,
            to_token=to_token,
            amount=amount
        )
        
        if not quote_data:
            await loading_msg.edit_text(
                f"❌ **Quote Not Available**\n\n"
                f"Could not get quote for {from_token} ➝ {to_token}\n\n"
                f"💡 Check token symbols and try again",
                parse_mode='Markdown'
            )
            return
        
        # Format and display quote
        quote_message = rango_swap_service.format_swap_quote(quote_data)
        quote_message += "\n\n💡 Use `/swap` to execute this trade"
        
        await loading_msg.edit_text(quote_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in swapquote command: {e}")
        await update.message.reply_text("❌ Failed to get swap quote. Please try again.")

async def swapsupported_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /swapsupported command to show supported chains and tokens"""
    try:
        await track_user_safely(update.effective_user)
        
        # Send loading message
        loading_msg = await update.message.reply_text("🔍 Loading supported chains and tokens...")
        
        # Load supported data
        await rango_swap_service.get_supported_blockchains()
        await rango_swap_service.get_supported_tokens()
        
        # Create inline keyboard for navigation
        keyboard = [
            [
                InlineKeyboardButton("🔗 Chains", callback_data="swap_supported_chains"),
                InlineKeyboardButton("💰 Tokens", callback_data="swap_supported_tokens")
            ],
            [InlineKeyboardButton("📚 Examples", callback_data="swap_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """🔁 **Rango Exchange Integration**

Cross-chain swaps powered by Rango Exchange, supporting 20+ blockchains and 1000+ tokens.

**Quick Examples:**
• `/swap ETH BNB 0.1` - Swap ETH to BNB
• `/swap BTC USDC 0.001` - Swap BTC to USDC  
• `/swap SOL MATIC 5.0` - Swap SOL to MATIC

**Available Commands:**
• `/swap` - Execute cross-chain swap
• `/swapquote` - Get price quote only
• `/swapsupported` - View supported assets

Use the buttons below to explore supported chains and tokens."""
        
        await loading_msg.edit_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in swapsupported command: {e}")
        await update.message.reply_text("❌ Failed to load supported assets. Please try again.")

async def price_monitoring_task(application):
    """Background task to monitor prices and send alerts"""
    logger.info("Price monitoring task started")
    
    while True:
        try:
            # Check for triggered alerts
            triggered_alerts = await alert_service.check_alerts_and_notify()
            
            # Send notifications for triggered alerts
            for alert in triggered_alerts:
                try:
                    user_id = int(alert['user_id'])
                    coin_symbol = alert['coin_symbol'].upper()
                    target_price = alert['target_price']
                    current_price = alert['current_price']
                    is_above = alert['is_above']
                    
                    # Create alert message
                    direction = "above" if is_above else "below"
                    message = (
                        f"🚨 **Price Alert Triggered!**\n\n"
                        f"**{coin_symbol}** has reached your target!\n\n"
                        f"💰 Current Price: ${current_price:,.2f}\n"
                        f"🎯 Target Price: ${target_price:,.2f} ({direction})\n\n"
                        f"The price is now {direction} your target threshold."
                    )
                    
                    # Send notification
                    await application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    logger.info(f"Alert notification sent to user {user_id} for {coin_symbol}")
                    
                except Exception as e:
                    logger.error(f"Error sending alert notification: {e}")
            
            # Check for live notifications to send
            pending_notifications = await live_notification_service.get_pending_notifications()
            
            for notif in pending_notifications:
                try:
                    user_id = int(notif['user_id'])
                    coin_id = notif['coin_id']
                    coin_symbol = notif['coin_symbol'].upper()
                    
                    # Get current price
                    price_data = await price_service.get_price(coin_id, ['usd'])
                    if price_data and 'usd' in price_data:
                        current_price = price_data['usd']
                        
                        # Create live notification message
                        message = (
                            f"**{coin_symbol}**: ${current_price:,.2f}\n"
                            f"🕐 {datetime.now().strftime('%H:%M:%S')}\n\n"
                            f"📡 Live Price Update"
                        )
                        
                        # Send live notification
                        await application.bot.send_message(
                            chat_id=user_id,
                            text=message,
                            parse_mode='Markdown'
                        )
                        
                        # Update last sent time
                        await live_notification_service.update_notification_sent(notif['id'])
                        
                        logger.info(f"Live notification sent to user {user_id} for {coin_symbol}")
                        
                except Exception as e:
                    logger.error(f"Error sending live notification: {e}")
            
            # Wait 1 minute before next check
            await asyncio.sleep(60)  # 1 minute
            
        except Exception as e:
            logger.error(f"Error in price monitoring task: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

if __name__ == '__main__':
    main()
