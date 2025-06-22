"""
Multi-Chain Wallet Service for generating and managing crypto wallets
Supports Ethereum, BSC, Polygon, Solana, and Tron networks
"""

import logging
import os
import json
import qrcode
from io import BytesIO
from typing import Dict, Optional, Tuple
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from cryptography.fernet import Fernet
from web3 import Web3
from solana.rpc.api import Client as SolanaClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from tronpy import Tron
from database import get_db, Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)

class UserWalletKeys(Base):
    """Model for storing encrypted user wallet keys"""
    __tablename__ = "user_wallet_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, unique=True, index=True)
    encrypted_mnemonic = Column(Text, nullable=False)
    eth_address = Column(String, nullable=False)
    solana_address = Column(String, nullable=False)
    tron_address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class MultiWalletService:
    """Service for multi-chain wallet creation and management"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.mnemo = Mnemonic("english")
        
        # Initialize Web3 connections (using public RPCs)
        self.eth_web3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))
        self.bsc_web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org"))
        self.polygon_web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
        
        # Initialize Solana client
        self.solana_client = SolanaClient("https://api.mainnet-beta.solana.com")
        
        # Initialize Tron client
        self.tron = Tron()
        
        logger.info("MultiWalletService initialized")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for wallet data"""
        key_file = "wallet_encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def generate_wallet(self, user_id: str) -> Dict:
        """
        Generate a new multi-chain wallet for user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with wallet addresses and mnemonic
        """
        try:
            # Check if user already has a wallet
            db = next(get_db())
            try:
                existing_wallet = db.query(UserWalletKeys).filter(
                    UserWalletKeys.user_id == user_id
                ).first()
                
                if existing_wallet:
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
                eth_private_key = bip44_addr_ctx.PrivateKey().Raw().ToHex()
                
                # Derive Solana address (BIP44 path: m/44'/501'/0'/0')
                bip44_sol_ctx = Bip44.FromSeed(seed, Bip44Coins.SOLANA)
                bip44_sol_acc = bip44_sol_ctx.Purpose().Coin().Account(0)
                bip44_sol_chg = bip44_sol_acc.Change(Bip44Changes.CHAIN_EXT)
                sol_private_key = bip44_sol_chg.PrivateKey().Raw().ToBytes()
                sol_keypair = Keypair.from_bytes(sol_private_key[:32])
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
                
            finally:
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
            
            logger.info(f"Generated new wallet for user {user_id}")
            return wallet_data
            
        except Exception as e:
            logger.error(f"Error generating wallet for user {user_id}: {e}")
            return {"error": f"Failed to generate wallet: {str(e)}"}
    
    def get_user_wallet(self, user_id: str) -> Optional[Dict]:
        """
        Get user's wallet addresses
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with wallet addresses or None
        """
        try:
            with get_db() as db:
                wallet = db.query(UserWalletKeys).filter(
                    UserWalletKeys.user_id == user_id,
                    UserWalletKeys.is_active == True
                ).first()
                
                if not wallet:
                    return None
                
                return {
                    "addresses": {
                        "ethereum": wallet.eth_address,
                        "bsc": wallet.eth_address,
                        "polygon": wallet.eth_address,
                        "solana": wallet.solana_address,
                        "tron": wallet.tron_address
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting wallet for user {user_id}: {e}")
            return None
    
    def get_wallet_balances(self, user_id: str) -> Optional[Dict]:
        """
        Get wallet balances for all chains
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with balances or None
        """
        try:
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                return None
                
            addresses = wallet["addresses"]
            balances = {}
            
            # Get Ethereum balance
            try:
                eth_balance = self.eth_web3.eth.get_balance(addresses["ethereum"])
                balances["ethereum"] = {
                    "balance": Web3.from_wei(eth_balance, "ether"),
                    "symbol": "ETH"
                }
            except Exception as e:
                balances["ethereum"] = {"balance": "Error", "symbol": "ETH"}
                logger.warning(f"Error getting ETH balance: {e}")
            
            # Get BSC balance
            try:
                bsc_balance = self.bsc_web3.eth.get_balance(addresses["bsc"])
                balances["bsc"] = {
                    "balance": Web3.from_wei(bsc_balance, "ether"),
                    "symbol": "BNB"
                }
            except Exception as e:
                balances["bsc"] = {"balance": "Error", "symbol": "BNB"}
                logger.warning(f"Error getting BNB balance: {e}")
            
            # Get Polygon balance
            try:
                matic_balance = self.polygon_web3.eth.get_balance(addresses["polygon"])
                balances["polygon"] = {
                    "balance": Web3.from_wei(matic_balance, "ether"),
                    "symbol": "MATIC"
                }
            except Exception as e:
                balances["polygon"] = {"balance": "Error", "symbol": "MATIC"}
                logger.warning(f"Error getting MATIC balance: {e}")
            
            # Get Solana balance
            try:
                sol_pubkey = Pubkey.from_string(addresses["solana"])
                sol_balance_response = self.solana_client.get_balance(sol_pubkey)
                sol_balance = sol_balance_response.value / 1_000_000_000  # Convert lamports to SOL
                balances["solana"] = {
                    "balance": sol_balance,
                    "symbol": "SOL"
                }
            except Exception as e:
                balances["solana"] = {"balance": "Error", "symbol": "SOL"}
                logger.warning(f"Error getting SOL balance: {e}")
            
            # Get Tron balance
            try:
                tron_balance = self.tron.get_account_balance(addresses["tron"])
                balances["tron"] = {
                    "balance": tron_balance,
                    "symbol": "TRX"
                }
            except Exception as e:
                balances["tron"] = {"balance": "Error", "symbol": "TRX"}
                logger.warning(f"Error getting TRX balance: {e}")
            
            return balances
            
        except Exception as e:
            logger.error(f"Error getting balances for user {user_id}: {e}")
            return None
    
    def generate_qr_code(self, address: str) -> BytesIO:
        """
        Generate QR code for wallet address
        
        Args:
            address: Wallet address
            
        Returns:
            BytesIO object containing QR code image
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(address)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        img.save(bio, format="PNG")
        bio.seek(0)
        return bio
    
    def get_decrypted_mnemonic(self, user_id: str) -> Optional[str]:
        """
        Get decrypted mnemonic for user (use with caution)
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Decrypted mnemonic phrase or None
        """
        try:
            with get_db() as db:
                wallet = db.query(UserWalletKeys).filter(
                    UserWalletKeys.user_id == user_id,
                    UserWalletKeys.is_active == True
                ).first()
                
                if not wallet:
                    return None
                
                decrypted_mnemonic = self.fernet.decrypt(
                    wallet.encrypted_mnemonic.encode()
                ).decode()
                
                return decrypted_mnemonic
                
        except Exception as e:
            logger.error(f"Error decrypting mnemonic for user {user_id}: {e}")
            return None