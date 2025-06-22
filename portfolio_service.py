"""
Portfolio Service for tracking wallet holdings across multiple blockchains
"""

import os
import logging
import aiohttp
import asyncio
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PortfolioService:
    """Service for fetching wallet portfolio data using Covalent API"""
    
    def __init__(self):
        self.covalent_api_key = os.environ.get('COVALENT_API_KEY')
        if not self.covalent_api_key:
            raise ValueError("COVALENT_API_KEY environment variable is required")
        
        self.session = None
        self.base_url = "https://api.covalenthq.com/v1"
        
        # Supported blockchain chain IDs
        self.chains = {
            'eth': {'id': 1, 'name': 'Ethereum', 'symbol': 'ETH'},
            'ethereum': {'id': 1, 'name': 'Ethereum', 'symbol': 'ETH'},
            'bsc': {'id': 56, 'name': 'BSC', 'symbol': 'BNB'},
            'polygon': {'id': 137, 'name': 'Polygon', 'symbol': 'MATIC'},
            'avalanche': {'id': 43114, 'name': 'Avalanche', 'symbol': 'AVAX'},
            'arbitrum': {'id': 42161, 'name': 'Arbitrum', 'symbol': 'ETH'}
        }
        
        # Cache for portfolio data (5 minutes)
        self.portfolio_cache = {}
        self.cache_duration = timedelta(minutes=5)
        
        logger.info("PortfolioService initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {
                'Authorization': f'Bearer {self.covalent_api_key}',
                'Content-Type': 'application/json'
            }
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    def validate_wallet_address(self, address: str) -> Tuple[bool, str]:
        """
        Validate wallet address format and return validation result with address type
        
        Returns:
            Tuple of (is_valid, address_type)
        """
        if not address:
            return False, "empty"
        
        # Remove any whitespace
        address = address.strip()
        
        # Check if it's a valid Ethereum address format (42 chars, starts with 0x)
        if re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return True, "ethereum"
        
        # Check if it's a TRON address (34 chars, starts with T)
        if re.match(r'^T[A-Za-z0-9]{33}$', address):
            return False, "tron"  # TRON not supported yet
        
        # Check if it's a Bitcoin address (various formats)
        if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address) or \
           re.match(r'^bc1[a-z0-9]{39,59}$', address):
            return False, "bitcoin"  # Bitcoin not supported
        
        return False, "unknown"
    
    def get_chain_info(self, chain_input: str) -> Optional[Dict]:
        """Get chain information from user input"""
        chain_input = chain_input.lower().strip()
        return self.chains.get(chain_input)
    
    def _get_cache_key(self, wallet_address: str, chain_id: int) -> str:
        """Generate cache key for portfolio data"""
        return f"{wallet_address}_{chain_id}"
    
    def _is_cache_valid(self, cached_data: Dict) -> bool:
        """Check if cached data is still valid"""
        if not cached_data:
            return False
        
        cache_time = cached_data.get('timestamp')
        if not cache_time:
            return False
        
        return datetime.now() - cache_time < self.cache_duration
    
    async def get_wallet_portfolio(self, wallet_address: str, chain: str = 'eth') -> Optional[Dict]:
        """
        Get portfolio data for a wallet address on specified chain
        
        Args:
            wallet_address: Wallet address to check
            chain: Blockchain to check (eth, bsc, polygon, etc.)
        
        Returns:
            Portfolio data dictionary or None if failed
        """
        try:
            # Validate wallet address
            if not self.validate_wallet_address(wallet_address):
                return {'error': 'Invalid wallet address format'}
            
            # Get chain info
            chain_info = self.get_chain_info(chain)
            if not chain_info:
                return {'error': f'Unsupported blockchain: {chain}'}
            
            chain_id = chain_info['id']
            
            # Check cache
            cache_key = self._get_cache_key(wallet_address, chain_id)
            cached_data = self.portfolio_cache.get(cache_key)
            
            if cached_data and self._is_cache_valid(cached_data):
                logger.info(f"Using cached portfolio data for {wallet_address}")
                return cached_data['data']
            
            # Fetch from API
            session = await self._get_session()
            url = f"{self.base_url}/{chain_id}/address/{wallet_address}/balances_v2/"
            params = {
                'quote-currency': 'USD',
                'format': 'JSON',
                'nft': 'false',
                'no-nft-fetch': 'true'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('error') or not data.get('data'):
                        logger.error(f"API error for {wallet_address}: {data.get('error_message', 'Unknown error')}")
                        return {'error': 'Unable to fetch portfolio data'}
                    
                    # Process the portfolio data
                    portfolio = self._process_portfolio_data(data['data'], chain_info)
                    
                    # Cache the result
                    self.portfolio_cache[cache_key] = {
                        'data': portfolio,
                        'timestamp': datetime.now()
                    }
                    
                    logger.info(f"Successfully fetched portfolio for {wallet_address} on {chain_info['name']}")
                    return portfolio
                    
                elif response.status == 401:
                    logger.error("Invalid Covalent API key")
                    return {'error': 'API authentication failed'}
                elif response.status == 429:
                    logger.warning("Rate limit hit for Covalent API")
                    return {'error': 'Rate limit exceeded. Please try again later.'}
                else:
                    logger.error(f"Failed to fetch portfolio: HTTP {response.status}")
                    return {'error': 'Failed to fetch portfolio data'}
                    
        except Exception as e:
            logger.error(f"Error fetching portfolio for {wallet_address}: {e}")
            return {'error': 'An error occurred while fetching portfolio data'}
    
    def _process_portfolio_data(self, data: Dict, chain_info: Dict) -> Dict:
        """Process raw Covalent API response into formatted portfolio data"""
        try:
            address = data.get('address', '')
            items = data.get('items', [])
            
            tokens = []
            total_value = 0.0
            
            for item in items:
                try:
                    # Skip tokens with zero balance
                    balance_raw = int(item.get('balance', '0'))
                    if balance_raw == 0:
                        continue
                    
                    # Get token info
                    contract_name = item.get('contract_name', 'Unknown')
                    contract_ticker_symbol = item.get('contract_ticker_symbol', '')
                    contract_decimals = item.get('contract_decimals', 18)
                    
                    # Calculate actual balance
                    balance = balance_raw / (10 ** contract_decimals)
                    
                    # Skip very small balances (less than $0.01)
                    if balance < 0.000001:
                        continue
                    
                    # Get USD value
                    quote = item.get('quote', 0) or 0
                    quote_rate = item.get('quote_rate', 0) or 0
                    
                    # Calculate 24h change
                    quote_rate_24h = item.get('quote_rate_24h', 0) or 0
                    price_change_24h = 0
                    if quote_rate_24h > 0 and quote_rate > 0:
                        price_change_24h = ((quote_rate - quote_rate_24h) / quote_rate_24h) * 100
                    
                    # Only include tokens with significant value (>$0.01)
                    if quote >= 0.01:
                        tokens.append({
                            'name': contract_name,
                            'symbol': contract_ticker_symbol.upper(),
                            'balance': balance,
                            'value_usd': quote,
                            'price_usd': quote_rate,
                            'price_change_24h': price_change_24h,
                            'contract_address': item.get('contract_address', '')
                        })
                        
                        total_value += quote
                
                except Exception as e:
                    logger.warning(f"Error processing token item: {e}")
                    continue
            
            # Sort tokens by USD value (highest first)
            tokens.sort(key=lambda x: x['value_usd'], reverse=True)
            
            return {
                'address': address,
                'chain': chain_info['name'],
                'chain_symbol': chain_info['symbol'],
                'tokens': tokens,
                'total_value': total_value,
                'token_count': len(tokens),
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing portfolio data: {e}")
            return {'error': 'Error processing portfolio data'}
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            asyncio.create_task(self.session.close())