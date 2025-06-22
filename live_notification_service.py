"""
Live Price Notification Service
Manages real-time cryptocurrency price notifications for users
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import sessionmaker
from database import engine, LiveNotification
from price_service import PriceService
from coin_mapper import CoinMapper

logger = logging.getLogger(__name__)

class LiveNotificationService:
    """Service for managing live price notifications"""
    
    def __init__(self):
        self.price_service = PriceService()
        self.coin_mapper = CoinMapper()
        logger.info("LiveNotificationService initialized")
    
    async def add_live_notification(self, user_id: str, coin_symbol: str) -> Dict:
        """Add a live price notification for a user"""
        try:
            # Map coin symbol to coin ID
            coin_id = self.coin_mapper.get_coin_id(coin_symbol.lower())
            if not coin_id:
                return {"success": False, "error": f"Cryptocurrency '{coin_symbol}' not found"}
            
            # Get a database session
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            try:
                # Check if notification already exists
                existing = db.query(LiveNotification).filter(
                    LiveNotification.user_id == user_id,
                    LiveNotification.coin_id == coin_id,
                    LiveNotification.is_active == True
                ).first()
                
                if existing:
                    return {"success": False, "error": f"Live notification for {coin_symbol.upper()} already exists"}
                
                # Create new notification
                notification = LiveNotification(
                    user_id=user_id,
                    coin_id=coin_id,
                    coin_symbol=coin_symbol.upper()
                )
                
                db.add(notification)
                db.commit()
                
                logger.info(f"Live notification added for user {user_id}: {coin_symbol}")
                return {"success": True, "coin_symbol": coin_symbol.upper()}
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error adding live notification: {e}")
            return {"success": False, "error": "Failed to add live notification"}
    
    async def remove_live_notification(self, user_id: str, coin_symbol: str = None) -> Dict:
        """Remove live price notification(s) for a user"""
        try:
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            try:
                if coin_symbol:
                    # Remove specific coin notification
                    coin_id = self.coin_mapper.get_coin_id(coin_symbol.lower())
                    if not coin_id:
                        return {"success": False, "error": f"Cryptocurrency '{coin_symbol}' not found"}
                    
                    notification = db.query(LiveNotification).filter(
                        LiveNotification.user_id == user_id,
                        LiveNotification.coin_id == coin_id,
                        LiveNotification.is_active == True
                    ).first()
                    
                    if not notification:
                        return {"success": False, "error": f"No live notification found for {coin_symbol.upper()}"}
                    
                    notification.is_active = False
                    db.commit()
                    
                    return {"success": True, "coin_symbol": coin_symbol.upper()}
                else:
                    # Remove all notifications for user
                    notifications = db.query(LiveNotification).filter(
                        LiveNotification.user_id == user_id,
                        LiveNotification.is_active == True
                    ).all()
                    
                    if not notifications:
                        return {"success": False, "error": "No active live notifications found"}
                    
                    for notification in notifications:
                        notification.is_active = False
                    
                    db.commit()
                    count = len(notifications)
                    return {"success": True, "count": count}
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error removing live notification: {e}")
            return {"success": False, "error": "Failed to remove live notification"}
    
    async def get_user_notifications(self, user_id: str) -> List[Dict]:
        """Get all active live notifications for a user"""
        try:
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            try:
                notifications = db.query(LiveNotification).filter(
                    LiveNotification.user_id == user_id,
                    LiveNotification.is_active == True
                ).all()
                
                return [
                    {
                        "id": notif.id,
                        "coin_id": notif.coin_id,
                        "coin_symbol": notif.coin_symbol,
                        "created_at": notif.created_at,
                        "last_sent": notif.last_sent
                    }
                    for notif in notifications
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return []
    
    async def get_pending_notifications(self) -> List[Dict]:
        """Get all notifications that need to be sent"""
        try:
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            try:
                # Get notifications that haven't been sent in the last minute
                one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
                
                notifications = db.query(LiveNotification).filter(
                    LiveNotification.is_active == True
                ).filter(
                    (LiveNotification.last_sent == None) | 
                    (LiveNotification.last_sent <= one_minute_ago)
                ).all()
                
                return [
                    {
                        "id": notif.id,
                        "user_id": notif.user_id,
                        "coin_id": notif.coin_id,
                        "coin_symbol": notif.coin_symbol
                    }
                    for notif in notifications
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting pending notifications: {e}")
            return []
    
    async def update_notification_sent(self, notification_id: int):
        """Update the last_sent timestamp for a notification"""
        try:
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            try:
                notification = db.query(LiveNotification).filter(
                    LiveNotification.id == notification_id
                ).first()
                
                if notification:
                    notification.last_sent = datetime.utcnow()
                    db.commit()
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error updating notification sent time: {e}")