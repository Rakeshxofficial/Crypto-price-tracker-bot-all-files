"""
Rango Exchange API Service for Cross-Chain Swaps
Provides real-time swap quotes and transaction execution
"""

import aiohttp
import asyncio
import logging
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class RangoSwapService:
    """Service for handling cross-chain swaps via Rango Exchange API"""
    
    def __init__(self):
        self.base_url = "https://api.rango.exchange"
        self.api_key = os.environ.get("RANGO_API_KEY")
        self.session = None
        self.supported_blockchains = {}
        self.supported_tokens = {}
        logger.info("RangoSwapService initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {"accept": "*/*"}
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self.session
    
    async def get_supported_blockchains(self) -> Dict:
        """Get list of supported blockchains from Rango API"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/basic/meta"
            
            params = {}
            if self.api_key:
                params['apiKey'] = self.api_key
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Store both blockchains and tokens from meta endpoint
                    if 'blockchains' in data:
                        self.supported_blockchains = {
                            blockchain['name'].lower(): blockchain 
                            for blockchain in data['blockchains']
                        }
                    if 'tokens' in data:
                        self.supported_tokens = {}
                        for token in data['tokens']:
                            blockchain = token.get('blockchain', '').lower()
                            if blockchain not in self.supported_tokens:
                                self.supported_tokens[blockchain] = {}
                            symbol = token.get('symbol', '').upper()
                            self.supported_tokens[blockchain][symbol] = token
                    
                    logger.info(f"Fetched {len(self.supported_blockchains)} blockchains and tokens for {len(self.supported_tokens)} chains")
                    return self.supported_blockchains
                else:
                    logger.error(f"Failed to fetch meta data: {response.status}")
                    error_text = await response.text()
                    logger.error(f"Error details: {error_text}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching supported blockchains: {e}")
            return {}
    
    async def get_supported_tokens(self) -> Dict:
        """Get list of supported tokens from Rango API"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/v1/meta/tokens"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Group tokens by blockchain for easier lookup
                    self.supported_tokens = {}
                    for token in data.get('tokens', []):
                        blockchain = token.get('blockchain', '').lower()
                        if blockchain not in self.supported_tokens:
                            self.supported_tokens[blockchain] = {}
                        
                        symbol = token.get('symbol', '').upper()
                        self.supported_tokens[blockchain][symbol] = token
                    
                    logger.info(f"Fetched tokens for {len(self.supported_tokens)} blockchains")
                    return self.supported_tokens
                else:
                    logger.error(f"Failed to fetch tokens: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching supported tokens: {e}")
            return {}
    
    async def get_swap_quote(self, from_token: str, to_token: str, amount: str, 
                           from_chain: str = None, to_chain: str = None) -> Optional[Dict]:
        """Get swap quote from Rango API"""
        try:
            # Ensure we have blockchain and token data
            if not self.supported_blockchains:
                await self.get_supported_blockchains()
            if not self.supported_tokens:
                await self.get_supported_tokens()
            
            # Find token details
            from_token_info = await self._find_token(from_token, from_chain)
            to_token_info = await self._find_token(to_token, to_chain)
            
            if not from_token_info or not to_token_info:
                logger.error(f"Token not found: {from_token} or {to_token}")
                return None
            
            session = await self._get_session()
            url = f"{self.base_url}/basic/swap"
            
            # Convert token amount to proper format
            from_decimals = from_token_info.get('decimals', 18)
            amount_in_units = str(int(float(amount) * (10 ** from_decimals)))
            
            # Format token identifiers for Rango API
            from_address = from_token_info.get('address')
            to_address = to_token_info.get('address')
            from_blockchain = from_token_info['blockchain']
            to_blockchain = to_token_info['blockchain']
            
            # For native tokens, use just the blockchain name
            if from_address is None:
                from_token_id = from_blockchain
            else:
                from_token_id = f"{from_blockchain}.{from_address}"
                
            if to_address is None:
                to_token_id = to_blockchain
            else:
                to_token_id = f"{to_blockchain}.{to_address}"
            
            params = {
                'from': from_token_id,
                'to': to_token_id,
                'amount': amount_in_units,
                'slippage': '1.0',
                'disableMultiTx': 'false'
            }
            
            if self.api_key:
                params['apiKey'] = self.api_key
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Swap quote fetched: {from_token} -> {to_token}")
                    return data
                else:
                    logger.error(f"Failed to get swap quote: {response.status}")
                    error_data = await response.text()
                    logger.error(f"Error details: {error_data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting swap quote: {e}")
            return None
    
    async def _find_token(self, token_symbol: str, blockchain: str = None) -> Optional[Dict]:
        """Find token information by symbol and optional blockchain"""
        if not self.supported_tokens:
            await self.get_supported_blockchains()  # This fetches both tokens and blockchains
        
        token_symbol = token_symbol.upper()
        
        # Handle common token name mappings
        token_mappings = {
            'TRON': 'TRX',
            'SOLANA': 'SOL',
            'ETHEREUM': 'ETH',
            'BITCOIN': 'BTC'
        }
        
        if token_symbol in token_mappings:
            token_symbol = token_mappings[token_symbol]
        
        logger.info(f"Looking for token: {token_symbol}")
        logger.info(f"Available chains: {list(self.supported_tokens.keys())}")
        
        if blockchain:
            blockchain = blockchain.lower()
            if blockchain in self.supported_tokens:
                if token_symbol in self.supported_tokens[blockchain]:
                    return self.supported_tokens[blockchain][token_symbol]
        else:
            # For native tokens, prioritize their native chains
            native_chain_priority = {
                'TRX': 'tron',
                'SOL': 'solana', 
                'ETH': 'eth',
                'BTC': 'btc',
                'BNB': 'bsc'
            }
            
            # First check native chain if token is a native token
            if token_symbol in native_chain_priority:
                preferred_chain = native_chain_priority[token_symbol]
                if preferred_chain in self.supported_tokens and token_symbol in self.supported_tokens[preferred_chain]:
                    token_data = self.supported_tokens[preferred_chain][token_symbol]
                    logger.info(f"Found native {token_symbol} on {preferred_chain}")
                    logger.info(f"Token data: {token_data}")
                    return token_data
            
            # Then search across all blockchains
            for chain, tokens in self.supported_tokens.items():
                logger.info(f"Checking chain {chain} with {len(tokens)} tokens")
                if token_symbol in tokens:
                    logger.info(f"Found {token_symbol} on {chain}")
                    return tokens[token_symbol]
        
        # Log available tokens for debugging
        for chain, tokens in list(self.supported_tokens.items())[:3]:  # Show first 3 chains
            logger.info(f"Chain {chain} has tokens: {list(tokens.keys())[:10]}")  # Show first 10 tokens
        
        return None
    
    async def create_transaction(self, quote_id: str, user_address: str, 
                               destination_address: str = None) -> Optional[Dict]:
        """Create transaction for swap execution"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/v1/transaction"
            
            data = {
                'requestId': quote_id,
                'userSettings': {
                    'slippage': '1.0',
                    'enableRefuel': False
                },
                'validations': {
                    'balance': True,
                    'fee': True
                }
            }
            
            if destination_address:
                data['userSettings']['destinationAddress'] = destination_address
            
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Transaction created for quote {quote_id}")
                    return result
                else:
                    logger.error(f"Failed to create transaction: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            return None
    
    def format_swap_quote(self, quote_data: Dict) -> str:
        """Format swap quote data into user-friendly message"""
        try:
            route = quote_data.get('route', {})
            if not route:
                return "❌ No swap route found"
            
            from_token = route.get('from', {})
            to_token = route.get('to', {})
            
            from_symbol = from_token.get('symbol', 'Unknown')
            to_symbol = to_token.get('symbol', 'Unknown')
            from_amount = route.get('inputAmount', '0')
            to_amount = route.get('outputAmount', '0')
            
            # Format amounts with proper decimals
            from_decimals = from_token.get('decimals', 18)
            to_decimals = to_token.get('decimals', 18)
            
            from_amount_formatted = float(from_amount) / (10 ** from_decimals)
            to_amount_formatted = float(to_amount) / (10 ** to_decimals)
            
            # Build route path
            path = route.get('path', [])
            route_path = " ➝ ".join([step.get('to', {}).get('blockchain', '') for step in path])
            
            # Get fees
            fees = []
            for step in path:
                fee = step.get('fee', {})
                if fee:
                    fee_token = fee.get('token', {}).get('symbol', '')
                    fee_amount = float(fee.get('amount', '0')) / (10 ** fee.get('token', {}).get('decimals', 18))
                    if fee_amount > 0:
                        fees.append(f"{fee_amount:.6f} {fee_token}")
            
            message = f"""🔁 **Swap Quote**

💰 **Trade:** {from_amount_formatted:.6f} {from_symbol} ➝ {to_amount_formatted:.6f} {to_symbol}

🛣️ **Route:** {route_path}

⛽ **Network Fees:** {', '.join(fees) if fees else 'Calculating...'}

🎯 **Slippage:** 1.0%

💡 Use the buttons below to proceed with this swap."""
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting swap quote: {e}")
            return "❌ Error formatting swap quote"
    
    def get_supported_chains_list(self) -> str:
        """Get formatted list of supported chains"""
        if not self.supported_blockchains:
            return "Loading supported chains..."
        
        chains = []
        for name, info in self.supported_blockchains.items():
            display_name = info.get('displayName', name)
            chains.append(f"• {display_name}")
        
        if len(chains) > 20:  # Limit display
            chains = chains[:20] + [f"... and {len(chains) - 20} more"]
        
        return "🔗 **Supported Chains:**\n\n" + "\n".join(chains)
    
    def get_popular_tokens_list(self) -> str:
        """Get formatted list of popular tokens"""
        popular_tokens = [
            "ETH", "BTC", "BNB", "MATIC", "SOL", "TRX", "USDC", "USDT", 
            "DAI", "WETH", "WBNB", "LINK", "UNI", "AAVE", "COMP"
        ]
        
        message = "💰 **Popular Tokens:**\n\n"
        for i in range(0, len(popular_tokens), 3):
            row = popular_tokens[i:i+3]
            message += " • ".join(row) + "\n"
        
        message += "\n💡 Use format: `/swap ETH BNB 0.1`"
        return message
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("RangoSwapService session closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            try:
                asyncio.create_task(self.session.close())
            except:
                pass