"""
Price Service - Handles cryptocurrency price fetching from CoinGecko API
"""

import asyncio
import logging
import aiohttp
from typing import Dict, Optional
from config import PRICE_ENDPOINT, SUPPORTED_CURRENCIES, DEFAULT_CURRENCIES, CURRENCY_SYMBOLS, API_TIMEOUT

logger = logging.getLogger(__name__)

class PriceService:
    """Service for fetching cryptocurrency prices from CoinGecko API."""
    
    def __init__(self):
        """Initialize the price service."""
        self.session = None
        logger.info("PriceService initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Telegram-Crypto-Bot/1.0',
                    'Accept': 'application/json'
                }
            )
        return self.session
    
    async def get_price(self, coin_id: str, currencies: list = None) -> Optional[Dict]:
        """
        Fetch cryptocurrency price from CoinGecko API.
        
        Args:
            coin_id (str): CoinGecko coin identifier
            currencies (list): List of currencies to fetch (default: ['usd', 'eur', 'inr'])
            
        Returns:
            dict: Price data or None if failed
        """
        if currencies is None:
            currencies = DEFAULT_CURRENCIES
        
        try:
            # Prepare API parameters
            params = {
                'ids': coin_id,
                'vs_currencies': ','.join(currencies),
                'include_last_updated_at': 'true'
            }
            
            logger.info(f"Fetching price for {coin_id} in {currencies}")
            
            # Make API request
            session = await self._get_session()
            async with session.get(PRICE_ENDPOINT, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract price data for the requested coin
                    if coin_id in data:
                        price_data = data[coin_id]
                        logger.info(f"Successfully fetched price for {coin_id}: {price_data}")
                        return price_data
                    else:
                        logger.error(f"Coin {coin_id} not found in API response")
                        return None
                        
                elif response.status == 404:
                    logger.error(f"Coin {coin_id} not found (404)")
                    return None
                    
                elif response.status == 429:
                    logger.warning("Rate limit exceeded (429), waiting before retry...")
                    await asyncio.sleep(5)  # Wait 5 seconds
                    
                    # Try one more time after delay
                    async with session.get(PRICE_ENDPOINT, params=params) as retry_response:
                        if retry_response.status == 200:
                            retry_data = await retry_response.json()
                            if coin_id in retry_data:
                                price_data = retry_data[coin_id]
                                logger.info(f"Successfully fetched price for {coin_id} after retry: {price_data}")
                                return price_data
                        logger.error("Rate limit retry failed")
                        return None
                    
                else:
                    logger.error(f"API request failed with status {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout while fetching price for {coin_id}")
            return None
            
        except aiohttp.ClientError as e:
            logger.error(f"Network error while fetching price for {coin_id}: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error while fetching price for {coin_id}: {e}")
            return None
    
    async def get_multiple_prices(self, coin_ids: list, currencies: list = None) -> Optional[Dict]:
        """
        Fetch prices for multiple cryptocurrencies.
        
        Args:
            coin_ids (list): List of CoinGecko coin identifiers
            currencies (list): List of currencies to fetch
            
        Returns:
            dict: Price data for all coins or None if failed
        """
        if not coin_ids:
            return None
            
        if currencies is None:
            currencies = SUPPORTED_CURRENCIES
        
        try:
            # Prepare API parameters
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': ','.join(currencies),
                'include_last_updated_at': 'true'
            }
            
            logger.info(f"Fetching prices for {len(coin_ids)} coins")
            
            # Make API request
            session = await self._get_session()
            async with session.get(PRICE_ENDPOINT, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully fetched prices for {len(data)} coins")
                    return data
                else:
                    logger.error(f"API request failed with status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching multiple prices: {e}")
            return None
    
    async def check_api_status(self) -> bool:
        """
        Check if CoinGecko API is accessible.
        
        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            session = await self._get_session()
            async with session.get(f"{PRICE_ENDPOINT}?ids=bitcoin&vs_currencies=usd") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"API status check failed: {e}")
            return False
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("PriceService session closed")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            asyncio.create_task(self.close())
