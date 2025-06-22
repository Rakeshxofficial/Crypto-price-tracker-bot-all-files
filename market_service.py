"""
Enhanced Market Service for trending coins, detailed market data, and portfolio tracking
"""

import aiohttp
import asyncio
import logging
import json
from typing import Dict, List, Optional
from config import API_TIMEOUT

logger = logging.getLogger(__name__)

class MarketService:
    """Enhanced service for market data, trending coins, and portfolio tracking"""
    
    def __init__(self):
        self.session = None
        self.base_url = "https://api.coingecko.com/api/v3"
        logger.info("MarketService initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
            )
        return self.session
    
    async def get_trending_coins(self) -> Optional[List[Dict]]:
        """Get trending cryptocurrencies from CoinGecko"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/search/trending"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    trending_coins = []
                    
                    for coin_data in data.get('coins', [])[:7]:  # Top 7 trending
                        coin = coin_data.get('item', {})
                        trending_coins.append({
                            'id': coin.get('id'),
                            'name': coin.get('name'),
                            'symbol': coin.get('symbol'),
                            'market_cap_rank': coin.get('market_cap_rank'),
                            'thumb': coin.get('thumb'),
                            'score': coin.get('score', 0)
                        })
                    
                    logger.info(f"Successfully fetched {len(trending_coins)} trending coins")
                    return trending_coins
                    
                elif response.status == 429:
                    logger.warning("Rate limit hit for trending coins")
                    await asyncio.sleep(3)
                    return None
                else:
                    logger.error(f"Failed to fetch trending coins: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
            return None
    
    async def get_detailed_coin_data(self, coin_id: str) -> Optional[Dict]:
        """Get detailed coin data including market metrics for AI analysis"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    market_data = data.get('market_data', {})
                    
                    detailed_data = {
                        'coin_id': coin_id,
                        'name': data.get('name'),
                        'symbol': data.get('symbol'),
                        'current_price': market_data.get('current_price', {}).get('usd', 0),
                        'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                        'market_cap_rank': market_data.get('market_cap_rank'),
                        'total_volume': market_data.get('total_volume', {}).get('usd', 0),
                        'price_change_percentage_24h': market_data.get('price_change_percentage_24h', 0),
                        'price_change_percentage_7d': market_data.get('price_change_percentage_7d', 0),
                        'price_change_percentage_30d': market_data.get('price_change_percentage_30d', 0),
                        'circulating_supply': market_data.get('circulating_supply', 0),
                        'max_supply': market_data.get('max_supply'),
                        'ath': market_data.get('ath', {}).get('usd', 0),
                        'ath_change_percentage': market_data.get('ath_change_percentage', {}).get('usd', 0),
                        'last_updated': market_data.get('last_updated')
                    }
                    
                    logger.info(f"Successfully fetched detailed data for {coin_id}")
                    return detailed_data
                    
                elif response.status == 429:
                    logger.warning(f"Rate limit hit for {coin_id}")
                    await asyncio.sleep(5)
                    return None
                else:
                    logger.error(f"Failed to fetch detailed data for {coin_id}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching detailed coin data for {coin_id}: {e}")
            return None
    
    async def get_market_overview(self) -> Optional[Dict]:
        """Get overall market overview data"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/global"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    global_data = data.get('data', {})
                    
                    overview = {
                        'total_market_cap_usd': global_data.get('total_market_cap', {}).get('usd', 0),
                        'total_volume_24h_usd': global_data.get('total_volume', {}).get('usd', 0),
                        'market_cap_change_percentage_24h': global_data.get('market_cap_change_percentage_24h_usd', 0),
                        'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                        'markets': global_data.get('markets', 0),
                        'btc_dominance': global_data.get('market_cap_percentage', {}).get('btc', 0),
                        'eth_dominance': global_data.get('market_cap_percentage', {}).get('eth', 0)
                    }
                    
                    logger.info("Successfully fetched market overview")
                    return overview
                    
                elif response.status == 429:
                    logger.warning("Rate limit hit for market overview")
                    await asyncio.sleep(3)
                    return None
                else:
                    logger.error(f"Failed to fetch market overview: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return None
    
    async def get_top_coins_by_market_cap(self, limit: int = 10) -> Optional[List[Dict]]:
        """Get top coins by market cap for daily summary"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h,7d'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully fetched top {len(data)} coins by market cap")
                    return data
                    
                elif response.status == 429:
                    logger.warning("Rate limit hit for top coins")
                    await asyncio.sleep(5)
                    return None
                else:
                    logger.error(f"Failed to fetch top coins: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching top coins: {e}")
            return None
    
    async def check_price_for_alerts(self, coin_ids: List[str]) -> Optional[Dict]:
        """Get current prices for multiple coins (for alert checking)"""
        try:
            if not coin_ids:
                return {}
                
            session = await self._get_session()
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd',
                'include_last_updated_at': 'true'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully fetched prices for {len(data)} coins for alerts")
                    return data
                    
                elif response.status == 429:
                    logger.warning("Rate limit hit for alert price check")
                    await asyncio.sleep(3)
                    return None
                else:
                    logger.error(f"Failed to fetch prices for alerts: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching prices for alerts: {e}")
            return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            asyncio.create_task(self.session.close())