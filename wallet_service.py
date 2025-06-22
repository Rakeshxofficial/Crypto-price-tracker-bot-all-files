"""
Wallet Service for managing user's saved wallet addresses
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal, UserWallet

logger = logging.getLogger(__name__)

class WalletService:
    """Service for managing user wallet addresses"""
    
    def __init__(self):
        logger.info("WalletService initialized")
    
    async def set_default_wallet(self, user_id: str, wallet_address: str, 
                                blockchain: str = 'eth', label: Optional[str] = None) -> bool:
        """Set a default wallet for a user"""
        try:
            db = SessionLocal()
            
            # Remove existing default wallet for this user
            existing_defaults = db.query(UserWallet).filter(
                UserWallet.user_id == user_id,
                UserWallet.is_default == True,
                UserWallet.is_active == True
            ).all()
            
            for wallet in existing_defaults:
                wallet.is_default = False
            
            # Check if this wallet already exists for the user
            existing_wallet = db.query(UserWallet).filter(
                UserWallet.user_id == user_id,
                UserWallet.wallet_address == wallet_address,
                UserWallet.blockchain == blockchain,
                UserWallet.is_active == True
            ).first()
            
            if existing_wallet:
                # Update existing wallet to be default
                existing_wallet.is_default = True
                existing_wallet.label = label
                logger.info(f"Updated existing wallet as default for user {user_id}")
            else:
                # Create new wallet entry
                new_wallet = UserWallet(
                    user_id=user_id,
                    wallet_address=wallet_address,
                    blockchain=blockchain,
                    label=label,
                    is_default=True,
                    is_active=True
                )
                db.add(new_wallet)
                logger.info(f"Created new default wallet for user {user_id}")
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error setting default wallet: {e}")
            return False
        finally:
            db.close()
    
    async def get_default_wallet(self, user_id: str) -> Optional[Dict]:
        """Get user's default wallet"""
        try:
            db = SessionLocal()
            wallet = db.query(UserWallet).filter(
                UserWallet.user_id == user_id,
                UserWallet.is_default == True,
                UserWallet.is_active == True
            ).first()
            
            if wallet:
                return {
                    'address': wallet.wallet_address,
                    'blockchain': wallet.blockchain,
                    'label': wallet.label,
                    'created_at': wallet.created_at
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting default wallet: {e}")
            return None
        finally:
            db.close()
    
    async def get_user_wallets(self, user_id: str) -> List[Dict]:
        """Get all active wallets for a user"""
        try:
            db = SessionLocal()
            wallets = db.query(UserWallet).filter(
                UserWallet.user_id == user_id,
                UserWallet.is_active == True
            ).order_by(UserWallet.is_default.desc(), UserWallet.created_at.desc()).all()
            
            wallet_list = []
            for wallet in wallets:
                wallet_list.append({
                    'id': wallet.id,
                    'address': wallet.wallet_address,
                    'blockchain': wallet.blockchain,
                    'label': wallet.label,
                    'is_default': wallet.is_default,
                    'created_at': wallet.created_at
                })
            
            return wallet_list
            
        except Exception as e:
            logger.error(f"Error getting user wallets: {e}")
            return []
        finally:
            db.close()
    
    async def remove_wallet(self, user_id: str, wallet_id: int) -> bool:
        """Remove a wallet from user's saved wallets"""
        try:
            db = SessionLocal()
            wallet = db.query(UserWallet).filter(
                UserWallet.id == wallet_id,
                UserWallet.user_id == user_id
            ).first()
            
            if wallet:
                wallet.is_active = False
                db.commit()
                logger.info(f"Removed wallet {wallet_id} for user {user_id}")
                return True
            else:
                logger.warning(f"Wallet {wallet_id} not found for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing wallet: {e}")
            return False
        finally:
            db.close()
    
    def truncate_address(self, address: str) -> str:
        """Truncate wallet address for display"""
        if len(address) > 10:
            return f"{address[:6]}...{address[-4:]}"
        return address