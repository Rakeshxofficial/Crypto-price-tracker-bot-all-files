"""
Currency Converter Service with Real-time Exchange Rates
Provides live currency conversion using ExchangeRate-API
"""

import asyncio
import logging
import aiohttp
from typing import Dict, Optional
from config import SUPPORTED_CURRENCIES, CURRENCY_SYMBOLS

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """Service for real-time currency conversion using ExchangeRate-API"""
    
    def __init__(self):
        """Initialize the currency converter service."""
        self.session = None
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        logger.info("CurrencyConverter initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Telegram-Crypto-Bot/1.0',
                    'Accept': 'application/json'
                }
            )
        return self.session
    
    async def get_exchange_rates(self, base_currency: str = 'USD') -> Optional[Dict]:
        """
        Get current exchange rates for a base currency
        
        Args:
            base_currency: Base currency code (e.g., 'USD')
        
        Returns:
            Dictionary with exchange rates or None if failed
        """
        try:
            base_currency = base_currency.upper()
            
            # Check cache first
            cache_key = f"rates_{base_currency}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                import time
                if time.time() - cached_data['timestamp'] < self.cache_duration:
                    logger.info(f"Using cached exchange rates for {base_currency}")
                    return cached_data['data']
            
            session = await self._get_session()
            url = f"{self.base_url}/{base_currency}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'rates' in data:
                        # Cache the result
                        import time
                        self.cache[cache_key] = {
                            'data': data,
                            'timestamp': time.time()
                        }
                        
                        logger.info(f"Successfully fetched exchange rates for {base_currency}")
                        return data
                    
                logger.warning(f"Invalid response format from exchange rate API")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {e}")
            return None
    
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Optional[Dict]:
        """
        Convert amount from one currency to another
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
        
        Returns:
            Dictionary with conversion result or None if failed
        """
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            # Validate currencies
            if from_currency not in [c.upper() for c in SUPPORTED_CURRENCIES]:
                return {'error': f'Unsupported source currency: {from_currency}'}
            
            if to_currency not in [c.upper() for c in SUPPORTED_CURRENCIES]:
                return {'error': f'Unsupported target currency: {to_currency}'}
            
            # If same currency, return original amount
            if from_currency == to_currency:
                return {
                    'amount': amount,
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'converted_amount': amount,
                    'exchange_rate': 1.0,
                    'timestamp': None
                }
            
            # Get exchange rates
            rates_data = await self.get_exchange_rates(from_currency)
            if not rates_data:
                return {'error': 'Unable to fetch current exchange rates'}
            
            # Extract exchange rate
            rates = rates_data.get('rates', {})
            if to_currency not in rates:
                return {'error': f'Exchange rate not available for {to_currency}'}
            
            exchange_rate = rates[to_currency]
            converted_amount = amount * exchange_rate
            
            return {
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': converted_amount,
                'exchange_rate': exchange_rate,
                'timestamp': rates_data.get('date'),
                'last_updated': rates_data.get('time_last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return {'error': f'Conversion failed: {str(e)}'}
    
    async def get_multiple_conversions(self, amount: float, from_currency: str, target_currencies: list) -> Dict:
        """
        Convert amount to multiple target currencies
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            target_currencies: List of target currency codes
        
        Returns:
            Dictionary with multiple conversion results
        """
        results = {}
        
        for to_currency in target_currencies:
            conversion = await self.convert_currency(amount, from_currency, to_currency)
            results[to_currency.upper()] = conversion
        
        return results
    
    def format_conversion_result(self, conversion: Dict) -> str:
        """Format conversion result into user-friendly message"""
        try:
            if 'error' in conversion:
                return f"❌ {conversion['error']}"
            
            amount = conversion['amount']
            from_currency = conversion['from_currency']
            to_currency = conversion['to_currency']
            converted_amount = conversion['converted_amount']
            exchange_rate = conversion['exchange_rate']
            
            # Get currency symbols
            from_symbol = CURRENCY_SYMBOLS.get(from_currency.lower(), from_currency)
            to_symbol = CURRENCY_SYMBOLS.get(to_currency.lower(), to_currency)
            
            # Format amounts based on currency
            if from_currency in ['JPY', 'KRW']:
                from_formatted = f"{from_symbol}{amount:,.0f}"
            else:
                from_formatted = f"{from_symbol}{amount:,.2f}"
            
            if to_currency in ['JPY', 'KRW']:
                to_formatted = f"{to_symbol}{converted_amount:,.0f}"
            else:
                to_formatted = f"{to_symbol}{converted_amount:,.2f}"
            
            # Build result message
            result = f"{from_formatted} {from_currency} = {to_formatted} {to_currency}"
            
            # Add exchange rate
            if exchange_rate != 1.0:
                result += f"\n📊 Rate: 1 {from_currency} = {exchange_rate:.4f} {to_currency}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error formatting conversion result: {e}")
            return "❌ Error formatting conversion result"
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.session.close())
                else:
                    loop.run_until_complete(self.session.close())
            except Exception:
                pass