"""
Alert Service for managing price alerts and notifications
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from database import SessionLocal, PriceAlert
from market_service import MarketService

logger = logging.getLogger(__name__)

class AlertService:
    """Service for managing price alerts and notifications"""
    
    def __init__(self):
        self.market_service = MarketService()
        logger.info("AlertService initialized")
    
    async def create_alert(self, user_id: str, coin_id: str, coin_symbol: str, 
                          target_price: float, is_above: bool = True) -> bool:
        """Create a new price alert for a user"""
        try:
            db = SessionLocal()
            
            # Check if user already has an alert for this coin
            existing_alert = db.query(PriceAlert).filter(
                PriceAlert.user_id == user_id,
                PriceAlert.coin_id == coin_id,
                PriceAlert.is_active == True
            ).first()
            
            if existing_alert:
                # Update existing alert
                existing_alert.target_price = target_price
                existing_alert.is_above = is_above
                existing_alert.created_at = datetime.utcnow()
                existing_alert.triggered_at = None
                logger.info(f"Updated alert for user {user_id}, coin {coin_id}")
            else:
                # Create new alert
                new_alert = PriceAlert(
                    user_id=user_id,
                    coin_id=coin_id,
                    coin_symbol=coin_symbol.upper(),
                    target_price=target_price,
                    is_above=is_above,
                    is_active=True
                )
                db.add(new_alert)
                logger.info(f"Created new alert for user {user_id}, coin {coin_id}")
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return False
        finally:
            db.close()
    
    async def get_user_alerts(self, user_id: str) -> List[Dict]:
        """Get all active alerts for a user"""
        try:
            db = SessionLocal()
            alerts = db.query(PriceAlert).filter(
                PriceAlert.user_id == user_id,
                PriceAlert.is_active == True
            ).all()
            
            alert_list = []
            for alert in alerts:
                alert_list.append({
                    'id': alert.id,
                    'coin_symbol': alert.coin_symbol,
                    'coin_id': alert.coin_id,
                    'target_price': alert.target_price,
                    'is_above': alert.is_above,
                    'created_at': alert.created_at
                })
            
            return alert_list
            
        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            return []
        finally:
            db.close()
    
    async def delete_alert(self, user_id: str, alert_id: int) -> bool:
        """Delete a specific alert"""
        try:
            db = SessionLocal()
            alert = db.query(PriceAlert).filter(
                PriceAlert.id == alert_id,
                PriceAlert.user_id == user_id
            ).first()
            
            if alert:
                alert.is_active = False
                db.commit()
                logger.info(f"Deleted alert {alert_id} for user {user_id}")
                return True
            else:
                logger.warning(f"Alert {alert_id} not found for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting alert: {e}")
            return False
        finally:
            db.close()
    
    async def check_alerts_and_notify(self) -> List[Dict]:
        """Check all active alerts and return triggered ones"""
        try:
            db = SessionLocal()
            active_alerts = db.query(PriceAlert).filter(
                PriceAlert.is_active == True,
                PriceAlert.triggered_at.is_(None)
            ).all()
            
            if not active_alerts:
                return []
            
            # Get unique coin IDs
            coin_ids = list(set([alert.coin_id for alert in active_alerts]))
            
            # Fetch current prices
            current_prices = await self.market_service.check_price_for_alerts(coin_ids)
            
            if not current_prices:
                logger.warning("Could not fetch prices for alert checking")
                return []
            
            triggered_alerts = []
            
            for alert in active_alerts:
                coin_data = current_prices.get(alert.coin_id, {})
                current_price = coin_data.get('usd', 0)
                
                if current_price <= 0:
                    continue
                
                # Check if alert should trigger
                should_trigger = False
                if alert.is_above and current_price >= alert.target_price:
                    should_trigger = True
                elif not alert.is_above and current_price <= alert.target_price:
                    should_trigger = True
                
                if should_trigger:
                    # Mark alert as triggered
                    alert.triggered_at = datetime.utcnow()
                    alert.is_active = False
                    
                    triggered_alerts.append({
                        'user_id': alert.user_id,
                        'coin_symbol': alert.coin_symbol,
                        'coin_id': alert.coin_id,
                        'target_price': alert.target_price,
                        'current_price': current_price,
                        'is_above': alert.is_above
                    })
                    
                    logger.info(f"Alert triggered for {alert.coin_symbol}: {current_price} vs {alert.target_price}")
            
            db.commit()
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
        finally:
            db.close()
    
    async def close(self):
        """Close connections"""
        await self.market_service.close()