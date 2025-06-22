"""
Coin Mapper - Maps user input to CoinGecko coin IDs
Handles various coin symbols and names for user convenience
"""

import logging

logger = logging.getLogger(__name__)

class CoinMapper:
    """Maps cryptocurrency symbols and names to CoinGecko IDs."""
    
    def __init__(self):
        """Initialize the coin mapping dictionary."""
        self.coin_map = {
            # Bitcoin
            'btc': 'bitcoin',
            'bitcoin': 'bitcoin',
            'xbt': 'bitcoin',
            
            # Ethereum
            'eth': 'ethereum',
            'ethereum': 'ethereum',
            'ether': 'ethereum',
            
            # Major Altcoins
            'sol': 'solana',
            'solana': 'solana',
            'ada': 'cardano',
            'cardano': 'cardano',
            'dot': 'polkadot',
            'polkadot': 'polkadot',
            'matic': 'matic-network',
            'polygon': 'matic-network',
            'avax': 'avalanche-2',
            'avalanche': 'avalanche-2',
            'luna': 'terra-luna',
            'atom': 'cosmos',
            'cosmos': 'cosmos',
            'near': 'near',
            'algo': 'algorand',
            'algorand': 'algorand',
            
            # Binance Ecosystem
            'bnb': 'binancecoin',
            'binancecoin': 'binancecoin',
            'cake': 'pancakeswap-token',
            'pancakeswap': 'pancakeswap-token',
            
            # DeFi Tokens
            'uni': 'uniswap',
            'uniswap': 'uniswap',
            'sushi': 'sushi',
            'sushiswap': 'sushi',
            'aave': 'aave',
            'comp': 'compound-governance-token',
            'compound': 'compound-governance-token',
            'mkr': 'maker',
            'maker': 'maker',
            'snx': 'havven',
            'synthetix': 'havven',
            'crv': 'curve-dao-token',
            'curve': 'curve-dao-token',
            
            # Layer 2 & Scaling
            'arb': 'arbitrum',
            'arbitrum': 'arbitrum',
            'op': 'optimism',
            'optimism': 'optimism',
            'lrc': 'loopring',
            'loopring': 'loopring',
            
            # Meme Coins
            'doge': 'dogecoin',
            'dogecoin': 'dogecoin',
            'shib': 'shiba-inu',
            'shiba': 'shiba-inu',
            'shiba-inu': 'shiba-inu',
            'pepe': 'pepe',
            
            # Traditional Crypto
            'ltc': 'litecoin',
            'litecoin': 'litecoin',
            'bch': 'bitcoin-cash',
            'bitcoin-cash': 'bitcoin-cash',
            'xrp': 'ripple',
            'ripple': 'ripple',
            'xlm': 'stellar',
            'stellar': 'stellar',
            'xmr': 'monero',
            'monero': 'monero',
            'zcash': 'zcash',
            'zec': 'zcash',
            'dash': 'dash',
            
            # Enterprise & Institutional
            'link': 'chainlink',
            'chainlink': 'chainlink',
            'vet': 'vechain',
            'vechain': 'vechain',
            'hbar': 'hedera-hashgraph',
            'hedera': 'hedera-hashgraph',
            'iota': 'iota',
            'miota': 'iota',
            
            # Gaming & NFT
            'mana': 'decentraland',
            'decentraland': 'decentraland',
            'sand': 'the-sandbox',
            'sandbox': 'the-sandbox',
            'axs': 'axie-infinity',
            'axie': 'axie-infinity',
            'gala': 'gala',
            'enjin': 'enjincoin',
            'enj': 'enjincoin',
            
            # Other Popular Coins
            'ftm': 'fantom',
            'fantom': 'fantom',
            'one': 'harmony',
            'harmony': 'harmony',
            'icx': 'icon',
            'icon': 'icon',
            'zil': 'zilliqa',
            'zilliqa': 'zilliqa',
            'eos': 'eos',
            'trx': 'tron',
            'tron': 'tron',
            'neo': 'neo',
            'ont': 'ontology',
            'ontology': 'ontology',
            'qtum': 'qtum',
            'waves': 'waves',
            'lsk': 'lisk',
            'lisk': 'lisk',
            
            # Stablecoins
            'usdt': 'tether',
            'tether': 'tether',
            'usdc': 'usd-coin',
            'usd-coin': 'usd-coin',
            'busd': 'binance-usd',
            'binance-usd': 'binance-usd',
            'dai': 'dai',
            'tusd': 'true-usd',
            'true-usd': 'true-usd',
            'pax': 'paxos-standard',
            'paxos': 'paxos-standard',
            'frax': 'frax',
            'fei': 'fei-usd',
            'tribe': 'tribe-2',
            
            # Top Market Cap Coins
            'xrp': 'ripple',
            'ripple': 'ripple',
            'doge': 'dogecoin',
            'dogecoin': 'dogecoin',
            'shib': 'shiba-inu',
            'shiba': 'shiba-inu',
            'shiba-inu': 'shiba-inu',
            'avax': 'avalanche-2',
            'avalanche': 'avalanche-2',
            'trx': 'tron',
            'tron': 'tron',
            'leo': 'leo-token',
            'leo-token': 'leo-token',
            'wbtc': 'wrapped-bitcoin',
            'wrapped-bitcoin': 'wrapped-bitcoin',
            'ltc': 'litecoin',
            'litecoin': 'litecoin',
            'etc': 'ethereum-classic',
            'ethereum-classic': 'ethereum-classic',
            'bch': 'bitcoin-cash',
            'bitcoin-cash': 'bitcoin-cash',
            'xlm': 'stellar',
            'stellar': 'stellar',
            'icp': 'internet-computer',
            'internet-computer': 'internet-computer',
            'hbar': 'hedera-hashgraph',
            'hedera': 'hedera-hashgraph',
            'ape': 'apecoin',
            'apecoin': 'apecoin',
            'qnt': 'quant-network',
            'quant': 'quant-network',
            'fil': 'filecoin',
            'filecoin': 'filecoin',
            'arb': 'arbitrum',
            'arbitrum': 'arbitrum',
            'ldo': 'lido-dao',
            'lido': 'lido-dao',
            'cro': 'crypto-com-chain',
            'cronos': 'crypto-com-chain',
            'vet': 'vechain',
            'vechain': 'vechain',
            'op': 'optimism',
            'optimism': 'optimism',
            'mana': 'decentraland',
            'decentraland': 'decentraland',
            'sand': 'the-sandbox',
            'sandbox': 'the-sandbox',
            'theta': 'theta-token',
            'tfuel': 'theta-fuel',
            'flow': 'flow',
            'iota': 'iota',
            'miota': 'iota',
            'xtz': 'tezos',
            'tezos': 'tezos',
            'egld': 'elrond-erd-2',
            'elrond': 'elrond-erd-2',
            'multivac': 'multivac',
            'klay': 'klay-token',
            'klaytn': 'klay-token',
            'axs': 'axie-infinity',
            'axie': 'axie-infinity',
            'aave': 'aave',
            'grt': 'the-graph',
            'graph': 'the-graph',
            'chz': 'chiliz',
            'chiliz': 'chiliz',
            'mkr': 'maker',
            'maker': 'maker',
            'snx': 'havven',
            'synthetix': 'havven',
            'eos': 'eos',
            'bsv': 'bitcoin-sv',
            'bitcoin-sv': 'bitcoin-sv',
            'neo': 'neo',
            'kcs': 'kucoin-shares',
            'kucoin': 'kucoin-shares',
            'gala': 'gala',
            'enj': 'enjincoin',
            'enjin': 'enjincoin',
            'bat': 'basic-attention-token',
            'brave': 'basic-attention-token',
            'zec': 'zcash',
            'zcash': 'zcash',
            'dash': 'dash',
            'xmr': 'monero',
            'monero': 'monero',
            'dcr': 'decred',
            'decred': 'decred',
            'btt': 'bittorrent',
            'bittorrent': 'bittorrent',
            'hot': 'holo',
            'holo': 'holo',
            'zil': 'zilliqa',
            'zilliqa': 'zilliqa',
            'cel': 'celsius-degree-token',
            'celsius': 'celsius-degree-token',
            'rvn': 'ravencoin',
            'ravencoin': 'ravencoin',
            'waves': 'waves',
            'ont': 'ontology',
            'ontology': 'ontology',
            'icx': 'icon',
            'icon': 'icon',
            'qtum': 'qtum',
            'omg': 'omisego',
            'omisego': 'omisego',
            'zrx': '0x',
            '0x': '0x',
            'nano': 'nano',
            'xno': 'nano',
            'sc': 'siacoin',
            'siacoin': 'siacoin',
            'dgb': 'digibyte',
            'digibyte': 'digibyte',
            'rep': 'augur',
            'augur': 'augur',
            'steem': 'steem',
            'lsk': 'lisk',
            'lisk': 'lisk',
            'storj': 'storj',
            'gno': 'gnosis',
            'gnosis': 'gnosis',
            'kmd': 'komodo',
            'komodo': 'komodo',
            'ark': 'ark',
            'ppt': 'populous',
            'populous': 'populous',
            'sys': 'syscoin',
            'syscoin': 'syscoin',
            'strat': 'stratis',
            'stratis': 'stratis',
            'lbc': 'lbry-credits',
            'lbry': 'lbry-credits',
            
            # Meme Coins
            'doge': 'dogecoin',
            'dogecoin': 'dogecoin',
            'shib': 'shiba-inu',
            'shiba': 'shiba-inu',
            'pepe': 'pepe',
            'floki': 'floki',
            'safemoon': 'safemoon-2',
            'babydoge': 'baby-doge-coin',
            'dogelon': 'dogelon-mars',
            'elon': 'dogelon-mars',
            'akita': 'akita-inu',
            'hokk': 'hokkaidu-inu',
            'kishu': 'kishu-inu',
            
            # Gaming & Metaverse
            'mana': 'decentraland',
            'sand': 'the-sandbox',
            'axs': 'axie-infinity',
            'gala': 'gala',
            'enj': 'enjincoin',
            'alice': 'myneighboralice',
            'tlm': 'alien-worlds',
            'slp': 'smooth-love-potion',
            'ygg': 'yield-guild-games',
            'ghst': 'aavegotchi',
            'radio': 'radiohead',
            'starl': 'starlink',
            'ufo': 'ufo-gaming',
            'revv': 'revuto',
            'tower': 'tower',
            'dar': 'mines-of-dalarnia',
            'pyr': 'vulcan-forged',
            
            # AI & Web3
            'fet': 'fetch-ai',
            'ocean': 'ocean-protocol',
            'agix': 'singularitynet',
            'rndr': 'render-token',
            'grt': 'the-graph',
            'ar': 'arweave',
            'storj': 'storj',
            'fil': 'filecoin',
            'sc': 'siacoin',
            'sia': 'siacoin',
            
            # TON Ecosystem
            'ton': 'the-open-network',
            'toncoin': 'the-open-network',
            'the-open-network': 'the-open-network',
            
            # Additional Popular DeFi & Solana Ecosystem
            'inj': 'injective-protocol',
            'injective': 'injective-protocol',
            'injective-protocol': 'injective-protocol',
            'ray': 'raydium',
            'raydium': 'raydium',
            'pyth': 'pyth-network',
            'pyth-network': 'pyth-network',
        }
        
        logger.info(f"CoinMapper initialized with {len(self.coin_map)} coin mappings")
    
    def get_coin_id(self, user_input: str) -> str:
        """
        Get CoinGecko coin ID from user input.
        
        Args:
            user_input (str): User's coin input (symbol or name)
            
        Returns:
            str: CoinGecko coin ID or None if not found
        """
        if not user_input:
            return None
            
        # Normalize input (lowercase, strip whitespace)
        normalized_input = user_input.lower().strip()
        
        # Direct lookup
        coin_id = self.coin_map.get(normalized_input)
        
        if coin_id:
            logger.info(f"Mapped '{user_input}' to '{coin_id}'")
            return coin_id
        
        # Try with common variations
        variations = [
            normalized_input.replace(' ', '-'),  # spaces to hyphens
            normalized_input.replace('-', ' '),  # hyphens to spaces
            normalized_input.replace('_', '-'),  # underscores to hyphens
        ]
        
        for variation in variations:
            coin_id = self.coin_map.get(variation)
            if coin_id:
                logger.info(f"Mapped '{user_input}' to '{coin_id}' via variation '{variation}'")
                return coin_id
        
        logger.warning(f"No mapping found for '{user_input}'")
        return None
    
    def get_supported_coins(self) -> list:
        """
        Get list of supported coin symbols and names.
        
        Returns:
            list: List of supported coin inputs
        """
        return list(self.coin_map.keys())
    
    def add_coin_mapping(self, user_input: str, coin_id: str) -> None:
        """
        Add a new coin mapping.
        
        Args:
            user_input (str): User input (symbol or name)
            coin_id (str): CoinGecko coin ID
        """
        normalized_input = user_input.lower().strip()
        self.coin_map[normalized_input] = coin_id
        logger.info(f"Added new mapping: '{user_input}' -> '{coin_id}'")
