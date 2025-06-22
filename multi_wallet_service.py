"""
Multi-chain Crypto Wallet Service
Supports Ethereum, BSC, Polygon, Solana, and Tron networks
Uses BIP39 mnemonic generation and BIP44 address derivation
"""

import os
import logging
from typing import Dict, Optional, List
from io import BytesIO
import base64
import aiohttp

# Cryptography imports
from cryptography.fernet import Fernet
from mnemonic import Mnemonic

# BIP utilities imports
from bip_utils import (
    Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
)

# Blockchain specific imports
from solders.keypair import Keypair
import qrcode

# Database imports
from database import get_db, UserWalletKeys

logger = logging.getLogger(__name__)

class MultiWalletService:
    """Service for managing multi-chain cryptocurrency wallets"""
    
    def __init__(self):
        """Initialize the multi-wallet service"""
        # Initialize mnemonic generator
        self.mnemo = Mnemonic("english")
        
        # Load or create encryption key for wallet storage
        self.encryption_key = self._load_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        
        logger.info("MultiWalletService initialized")
    
    def _load_encryption_key(self) -> bytes:
        """Load or create encryption key for wallet data"""
        key_file = "wallet_encryption.key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    async def create_wallet(self, user_id: str) -> Dict:
        """
        Create a new multi-chain wallet for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with wallet addresses and mnemonic
        """
        try:
            # Check if user already has a wallet
            db = next(get_db())
            existing_wallet = db.query(UserWalletKeys).filter(
                UserWalletKeys.user_id == user_id
            ).first()
            
            if existing_wallet:
                db.close()
                return {"error": "You already have a wallet. Use /mywallet to view it."}
            
            # Generate new mnemonic phrase
            mnemonic_phrase = self.mnemo.generate(strength=128)  # 12 words
            seed = Bip39SeedGenerator(mnemonic_phrase).Generate()
            
            # Derive Ethereum/BSC/Polygon address (BIP44 path: m/44'/60'/0'/0/0)
            bip44_mst_ctx = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
            bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
            bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
            bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)
            eth_address = bip44_addr_ctx.PublicKey().ToAddress()
            
            # Derive Solana address (BIP44 path: m/44'/501'/0'/0')
            bip44_sol_ctx = Bip44.FromSeed(seed, Bip44Coins.SOLANA)
            bip44_sol_acc = bip44_sol_ctx.Purpose().Coin().Account(0)
            bip44_sol_chg = bip44_sol_acc.Change(Bip44Changes.CHAIN_EXT)
            sol_private_key = bip44_sol_chg.PrivateKey().Raw().ToBytes()
            # For Solana, create keypair from 32-byte seed only
            sol_keypair = Keypair.from_seed(sol_private_key[:32])
            sol_address = str(sol_keypair.pubkey())
            
            # Derive Tron address (BIP44 path: m/44'/195'/0'/0/0)
            bip44_tron_ctx = Bip44.FromSeed(seed, Bip44Coins.TRON)
            bip44_tron_acc = bip44_tron_ctx.Purpose().Coin().Account(0)
            bip44_tron_chg = bip44_tron_acc.Change(Bip44Changes.CHAIN_EXT)
            bip44_tron_addr = bip44_tron_chg.AddressIndex(0)
            tron_address = bip44_tron_addr.PublicKey().ToAddress()
            
            # Encrypt and store wallet data
            encrypted_mnemonic = self.fernet.encrypt(mnemonic_phrase.encode()).decode()
            
            # Store wallet data
            wallet_record = UserWalletKeys(
                user_id=user_id,
                encrypted_mnemonic=encrypted_mnemonic,
                eth_address=eth_address,
                solana_address=sol_address,
                tron_address=tron_address
            )
            db.add(wallet_record)
            db.commit()
            db.close()
            
            wallet_data = {
                "mnemonic": mnemonic_phrase,
                "addresses": {
                    "ethereum": eth_address,
                    "bsc": eth_address,  # Same address for EVM chains
                    "polygon": eth_address,  # Same address for EVM chains
                    "solana": sol_address,
                    "tron": tron_address
                }
            }
            
            logger.info(f"Created new wallet for user {user_id}")
            return wallet_data
            
        except Exception as e:
            logger.error(f"Error generating wallet for user {user_id}: {e}")
            return {"error": "Failed to generate wallet. Please try again."}
    
    async def get_wallet(self, user_id: str) -> Optional[Dict]:
        """
        Get wallet information for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with wallet addresses or None
        """
        try:
            db = next(get_db())
            wallet = db.query(UserWalletKeys).filter(
                UserWalletKeys.user_id == user_id,
                UserWalletKeys.is_active == True
            ).first()
            
            if not wallet:
                db.close()
                return None
            
            result = {
                "addresses": {
                    "ethereum": wallet.eth_address,
                    "bsc": wallet.eth_address,
                    "polygon": wallet.eth_address,
                    "solana": wallet.solana_address,
                    "tron": wallet.tron_address
                }
            }
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting wallet for user {user_id}: {e}")
            return None
    
    async def get_wallet_with_mnemonic(self, user_id: str) -> Optional[Dict]:
        """
        Get wallet information including decrypted mnemonic
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with wallet addresses and mnemonic or None
        """
        try:
            db = next(get_db())
            wallet = db.query(UserWalletKeys).filter(
                UserWalletKeys.user_id == user_id,
                UserWalletKeys.is_active == True
            ).first()
            
            if not wallet:
                db.close()
                return None
            
            # Decrypt mnemonic
            decrypted_mnemonic = self.fernet.decrypt(wallet.encrypted_mnemonic.encode()).decode()
            
            result = {
                "mnemonic": decrypted_mnemonic,
                "addresses": {
                    "ethereum": wallet.eth_address,
                    "bsc": wallet.eth_address,
                    "polygon": wallet.eth_address,
                    "solana": wallet.solana_address,
                    "tron": wallet.tron_address
                }
            }
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting wallet with mnemonic for user {user_id}: {e}")
            return None
    
    def generate_qr_code(self, address: str) -> bytes:
        """
        Generate QR code for wallet address
        
        Args:
            address: Wallet address
            
        Returns:
            QR code image as bytes
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(address)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None
    
    async def get_wallet_balances(self, user_id: str) -> Optional[Dict]:
        """
        Get wallet balances across all supported chains
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with balances or None
        """
        try:
            wallet = await self.get_wallet(user_id)
            if not wallet:
                return None
            
            addresses = wallet["addresses"]
            balances = {}
            
            # Get Ethereum balance
            try:
                eth_balance = await self._get_ethereum_balance(addresses["ethereum"])
                balances["ethereum"] = {"balance": f"{eth_balance:.6f}", "symbol": "ETH"}
            except Exception as e:
                logger.error(f"Error fetching Ethereum balance: {e}")
                balances["ethereum"] = {"balance": "Error", "symbol": "ETH"}
            
            # Get BSC balance
            try:
                bsc_balance = await self._get_bsc_balance(addresses["bsc"])
                balances["bsc"] = {"balance": f"{bsc_balance:.6f}", "symbol": "BNB"}
            except Exception as e:
                logger.error(f"Error fetching BSC balance: {e}")
                balances["bsc"] = {"balance": "Error", "symbol": "BNB"}
            
            # Get Polygon balance
            try:
                matic_balance = await self._get_polygon_balance(addresses["polygon"])
                balances["polygon"] = {"balance": f"{matic_balance:.6f}", "symbol": "MATIC"}
            except Exception as e:
                logger.error(f"Error fetching Polygon balance: {e}")
                balances["polygon"] = {"balance": "Error", "symbol": "MATIC"}
            
            # Get Solana balance
            try:
                sol_balance = await self._get_solana_balance(addresses["solana"])
                balances["solana"] = {"balance": f"{sol_balance:.6f}", "symbol": "SOL"}
            except Exception as e:
                logger.error(f"Error fetching Solana balance: {e}")
                balances["solana"] = {"balance": "Error", "symbol": "SOL"}
            
            # Get Tron balance
            try:
                trx_balance = await self._get_tron_balance(addresses["tron"])
                balances["tron"] = {"balance": f"{trx_balance:.6f}", "symbol": "TRX"}
            except Exception as e:
                logger.error(f"Error fetching Tron balance: {e}")
                balances["tron"] = {"balance": "Error", "symbol": "TRX"}
            
            return balances
            
        except Exception as e:
            logger.error(f"Error getting wallet balances for user {user_id}: {e}")
            return None
    
    async def _get_ethereum_balance(self, address: str) -> float:
        """Get Ethereum balance via public RPC"""
        try:
            session = await self._get_session()
            url = "https://eth-mainnet.public.blastapi.io"
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    balance_wei = int(data["result"], 16)
                    return balance_wei / 10**18  # Convert from wei to ETH
                return 0.0
        except Exception:
            return 0.0
    
    async def _get_bsc_balance(self, address: str) -> float:
        """Get BSC balance via public RPC"""
        try:
            session = await self._get_session()
            url = "https://bsc-dataseed.binance.org"
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    balance_wei = int(data["result"], 16)
                    return balance_wei / 10**18  # Convert from wei to BNB
                return 0.0
        except Exception:
            return 0.0
    
    async def _get_polygon_balance(self, address: str) -> float:
        """Get Polygon balance via public RPC"""
        try:
            session = await self._get_session()
            url = "https://polygon-rpc.com"
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    balance_wei = int(data["result"], 16)
                    return balance_wei / 10**18  # Convert from wei to MATIC
                return 0.0
        except Exception:
            return 0.0
    
    async def _get_solana_balance(self, address: str) -> float:
        """Get Solana balance via public RPC"""
        try:
            session = await self._get_session()
            url = "https://api.mainnet-beta.solana.com"
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [address]
            }
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    balance_lamports = data["result"]["value"]
                    return balance_lamports / 10**9  # Convert from lamports to SOL
                return 0.0
        except Exception:
            return 0.0
    
    async def _get_tron_balance(self, address: str) -> float:
        """Get Tron balance via TronGrid API"""
        try:
            session = await self._get_session()
            url = f"https://api.trongrid.io/v1/accounts/{address}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "data" in data and data["data"]:
                        balance_sun = data["data"][0].get("balance", 0)
                        return balance_sun / 10**6  # Convert from SUN to TRX
                return 0.0
        except Exception:
            return 0.0
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not hasattr(self, '_session') or self._session.closed:
            import aiohttp
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def delete_wallet(self, user_id: str) -> bool:
        """
        Delete/deactivate wallet for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Success status
        """
        try:
            db = next(get_db())
            wallet = db.query(UserWalletKeys).filter(
                UserWalletKeys.user_id == user_id,
                UserWalletKeys.is_active == True
            ).first()
            
            if wallet:
                wallet.is_active = False
                db.commit()
                db.close()
                logger.info(f"Deactivated wallet for user {user_id}")
                return True
            
            db.close()
            return False
            
        except Exception as e:
            logger.error(f"Error deleting wallet for user {user_id}: {e}")
            return False
    
    async def send_transaction(self, user_id: str, chain: str, to_address: str, amount: float) -> Dict:
        """
        Send cryptocurrency transaction
        
        Args:
            user_id: Telegram user ID
            chain: Blockchain network (ethereum, bsc, polygon, solana, tron)
            to_address: Recipient address
            amount: Amount to send
            
        Returns:
            Transaction result dictionary
        """
        try:
            wallet_data = await self.get_wallet_with_mnemonic(user_id)
            if not wallet_data:
                return {"success": False, "error": "Wallet not found"}
            
            addresses = wallet_data["addresses"]
            mnemonic = wallet_data["mnemonic"]
            
            if chain == "tron":
                return await self._send_tron_transaction(mnemonic, addresses["tron"], to_address, amount)
            elif chain == "ethereum":
                return await self._send_ethereum_transaction(mnemonic, addresses["ethereum"], to_address, amount)
            elif chain == "bsc":
                return await self._send_bsc_transaction(mnemonic, addresses["bsc"], to_address, amount)
            elif chain == "polygon":
                return await self._send_polygon_transaction(mnemonic, addresses["polygon"], to_address, amount)
            elif chain == "solana":
                return await self._send_solana_transaction(mnemonic, addresses["solana"], to_address, amount)
            else:
                return {"success": False, "error": "Unsupported blockchain"}
                
        except Exception as e:
            logger.error(f"Error sending transaction for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_tron_transaction(self, mnemonic: str, from_address: str, to_address: str, amount: float) -> Dict:
        """Send TRX transaction"""
        try:
            from tronpy import Tron
            from tronpy.keys import PrivateKey
            import os
            
            # Generate private key from mnemonic
            seed = Mnemonic("english").to_seed(mnemonic)
            bip44_tron_ctx = Bip44.FromSeed(seed, Bip44Coins.TRON)
            bip44_tron_acc = bip44_tron_ctx.Purpose().Coin().Account(0)
            bip44_tron_chg = bip44_tron_acc.Change(Bip44Changes.CHAIN_EXT)
            bip44_tron_addr = bip44_tron_chg.AddressIndex(0)
            private_key_hex = bip44_tron_addr.PrivateKey().Raw().ToHex()
            
            # Initialize Tron client with API key
            tron_api_key = os.environ.get("TRON_API_KEY")
            if tron_api_key:
                from tronpy.providers import HTTPProvider
                provider = HTTPProvider(api_key=tron_api_key)
                client = Tron(provider=provider)
            else:
                client = Tron()
            priv_key = PrivateKey(bytes.fromhex(private_key_hex))
            
            # Convert amount to SUN (1 TRX = 1,000,000 SUN)
            amount_sun = int(amount * 1_000_000)
            
            # Create and sign transaction
            txn = (
                client.trx.transfer(from_address, to_address, amount_sun)
                .memo("Sent via Crypto Bot")
                .build()
                .sign(priv_key)
            )
            
            # Broadcast transaction
            result = txn.broadcast()
            
            return {
                "success": True,
                "tx_hash": result["txid"],
                "amount": amount,
                "from": from_address,
                "to": to_address,
                "chain": "tron"
            }
            
        except Exception as e:
            logger.error(f"Error sending Tron transaction: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_ethereum_transaction(self, mnemonic: str, from_address: str, to_address: str, amount: float) -> Dict:
        """Send ETH transaction"""
        try:
            from web3 import Web3
            
            # Connect to Ethereum network
            w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.public.blastapi.io'))
            
            # Generate private key from mnemonic
            seed = Mnemonic("english").to_seed(mnemonic)
            bip44_ctx = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
            bip44_acc_ctx = bip44_ctx.Purpose().Coin().Account(0)
            bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
            bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)
            private_key = bip44_addr_ctx.PrivateKey().Raw().ToBytes()
            
            # Get account from private key
            account = w3.eth.account.from_key(private_key)
            
            # Get nonce and gas price
            nonce = w3.eth.get_transaction_count(from_address)
            gas_price = w3.eth.gas_price
            
            # Convert amount to wei
            amount_wei = w3.to_wei(amount, 'ether')
            
            # Create transaction
            transaction = {
                'to': to_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
            }
            
            # Sign and send transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "amount": amount,
                "from": from_address,
                "to": to_address,
                "chain": "ethereum"
            }
            
        except Exception as e:
            logger.error(f"Error sending Ethereum transaction: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_bsc_transaction(self, mnemonic: str, from_address: str, to_address: str, amount: float) -> Dict:
        """Send BNB transaction on BSC"""
        try:
            from web3 import Web3
            
            # Connect to BSC network
            w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org'))
            
            # Generate private key from mnemonic (same as Ethereum)
            seed = Mnemonic("english").to_seed(mnemonic)
            bip44_ctx = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
            bip44_acc_ctx = bip44_ctx.Purpose().Coin().Account(0)
            bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
            bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)
            private_key = bip44_addr_ctx.PrivateKey().Raw().ToBytes()
            
            # Get account from private key
            account = w3.eth.account.from_key(private_key)
            
            # Get nonce and gas price
            nonce = w3.eth.get_transaction_count(from_address)
            gas_price = w3.eth.gas_price
            
            # Convert amount to wei
            amount_wei = w3.to_wei(amount, 'ether')
            
            # Create transaction
            transaction = {
                'to': to_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': 56  # BSC Chain ID
            }
            
            # Sign and send transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "amount": amount,
                "from": from_address,
                "to": to_address,
                "chain": "bsc"
            }
            
        except Exception as e:
            logger.error(f"Error sending BSC transaction: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_polygon_transaction(self, mnemonic: str, from_address: str, to_address: str, amount: float) -> Dict:
        """Send MATIC transaction on Polygon"""
        try:
            from web3 import Web3
            
            # Connect to Polygon network
            w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
            
            # Generate private key from mnemonic (same as Ethereum)
            seed = Mnemonic("english").to_seed(mnemonic)
            bip44_ctx = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
            bip44_acc_ctx = bip44_ctx.Purpose().Coin().Account(0)
            bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
            bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)
            private_key = bip44_addr_ctx.PrivateKey().Raw().ToBytes()
            
            # Get account from private key
            account = w3.eth.account.from_key(private_key)
            
            # Get nonce and gas price
            nonce = w3.eth.get_transaction_count(from_address)
            gas_price = w3.eth.gas_price
            
            # Convert amount to wei
            amount_wei = w3.to_wei(amount, 'ether')
            
            # Create transaction
            transaction = {
                'to': to_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': 137  # Polygon Chain ID
            }
            
            # Sign and send transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "amount": amount,
                "from": from_address,
                "to": to_address,
                "chain": "polygon"
            }
            
        except Exception as e:
            logger.error(f"Error sending Polygon transaction: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_solana_transaction(self, mnemonic: str, from_address: str, to_address: str, amount: float) -> Dict:
        """Send SOL transaction"""
        try:
            from solana.rpc.api import Client
            from solana.transaction import Transaction
            from solana.system_program import transfer, TransferParams
            from solders.keypair import Keypair
            from solders.pubkey import Pubkey
            
            # Connect to Solana network
            client = Client("https://api.mainnet-beta.solana.com")
            
            # Generate keypair from mnemonic
            seed = Mnemonic("english").to_seed(mnemonic)
            bip44_sol_ctx = Bip44.FromSeed(seed, Bip44Coins.SOLANA)
            bip44_sol_acc = bip44_sol_ctx.Purpose().Coin().Account(0)
            bip44_sol_chg = bip44_sol_acc.Change(Bip44Changes.CHAIN_EXT)
            sol_private_key = bip44_sol_chg.PrivateKey().Raw().ToBytes()
            
            # Create keypair
            keypair = Keypair.from_seed(sol_private_key[:32])
            
            # Convert amount to lamports
            amount_lamports = int(amount * 1_000_000_000)
            
            # Create transaction
            transfer_instruction = transfer(
                TransferParams(
                    from_pubkey=keypair.pubkey(),
                    to_pubkey=Pubkey.from_string(to_address),
                    lamports=amount_lamports
                )
            )
            
            transaction = Transaction().add(transfer_instruction)
            
            # Send transaction
            result = client.send_transaction(transaction, keypair)
            
            return {
                "success": True,
                "tx_hash": str(result.value),
                "amount": amount,
                "from": from_address,
                "to": to_address,
                "chain": "solana"
            }
            
        except Exception as e:
            logger.error(f"Error sending Solana transaction: {e}")
            return {"success": False, "error": str(e)}