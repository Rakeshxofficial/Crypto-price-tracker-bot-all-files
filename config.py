"""
Configuration settings for the Telegram Crypto Price Bot
"""

import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Telegram Bot Token (required)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is required!")
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable must be set")

# CoinGecko API Configuration
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
PRICE_ENDPOINT = f"{COINGECKO_BASE_URL}/simple/price"

# Supported currencies - Major global fiat currencies
SUPPORTED_CURRENCIES = [
    'usd',  # US Dollar
    'eur',  # Euro
    'gbp',  # British Pound
    'jpy',  # Japanese Yen
    'cad',  # Canadian Dollar
    'aud',  # Australian Dollar
    'chf',  # Swiss Franc
    'cny',  # Chinese Yuan
    'inr',  # Indian Rupee
    'krw',  # South Korean Won
    'sgd',  # Singapore Dollar
    'hkd',  # Hong Kong Dollar
    'nzd',  # New Zealand Dollar
    'sek',  # Swedish Krona
    'nok',  # Norwegian Krone
    'dkk',  # Danish Krone
    'pln',  # Polish Zloty
    'rub',  # Russian Ruble
    'brl',  # Brazilian Real
    'mxn',  # Mexican Peso
    'zar',  # South African Rand
    'try',  # Turkish Lira
    'aed',  # UAE Dirham
    'sar'   # Saudi Riyal
]

# Currency symbols mapping for display
CURRENCY_SYMBOLS = {
    'usd': '$',
    'eur': '€',
    'gbp': '£',
    'jpy': '¥',
    'cad': 'C$',
    'aud': 'A$',
    'chf': 'CHF',
    'cny': '¥',
    'inr': '₹',
    'krw': '₩',
    'sgd': 'S$',
    'hkd': 'HK$',
    'nzd': 'NZ$',
    'sek': 'kr',
    'nok': 'kr',
    'dkk': 'kr',
    'pln': 'zł',
    'rub': '₽',
    'brl': 'R$',
    'mxn': 'MX$',
    'zar': 'R',
    'try': '₺',
    'aed': 'د.إ',
    'sar': '﷼'
}

# Default currencies for price display
DEFAULT_CURRENCIES = ['usd', 'eur', 'inr']

# API timeout settings
API_TIMEOUT = 10  # seconds

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 50

logger.info("Configuration loaded successfully")
