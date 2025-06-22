"""
User Service for tracking bot users and analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func
from database import SessionLocal, BotUser

logger = logging.getLogger(__name__)

class UserService:
    """Service for tracking and managing bot users"""
    
    def __init__(self):
        """Initialize the user service."""
        logger.info("UserService initialized")
    
    async def track_user(self, user_id: str, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """
        Track a user interaction, creating new user record if needed
        
        Args:
            user_id: Telegram user ID
            username: Telegram username (optional)
            first_name: User's first name (optional)
            last_name: User's last name (optional)
        
        Returns:
            True if user was tracked successfully
        """
        db = None
        try:
            # Create a new session for each request to avoid connection issues
            db = SessionLocal()
            
            # Check if user already exists with timeout and retry logic
            existing_user = db.query(BotUser).filter(BotUser.user_id == user_id).first()
            
            if existing_user:
                # Update existing user
                existing_user.last_interaction = datetime.utcnow()
                existing_user.total_commands += 1
                
                # Update user info if provided
                if username:
                    existing_user.username = username
                if first_name:
                    existing_user.first_name = first_name
                if last_name:
                    existing_user.last_name = last_name
                
                db.commit()
                logger.debug(f"Updated user {user_id} interaction")
            else:
                # Create new user
                new_user = BotUser(
                    user_id=user_id,
                    username=username or "",
                    first_name=first_name or "",
                    last_name=last_name or "",
                    first_interaction=datetime.utcnow(),
                    last_interaction=datetime.utcnow(),
                    total_commands=1,
                    is_active=True
                )
                
                db.add(new_user)
                db.commit()
                logger.info(f"Registered new user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking user {user_id}: {e}")
            if db:
                try:
                    db.rollback()
                    db.close()
                except Exception:
                    pass
            return False
        finally:
            if db:
                try:
                    db.close()
                except Exception:
                    pass
    
    async def get_total_users(self) -> Dict:
        """
        Get total user statistics
        
        Returns:
            Dictionary containing user statistics
        """
        db = None
        try:
            db = SessionLocal()
            
            # Total unique users
            total_users = db.query(BotUser).count()
            
            # Active users (users who have interacted in the last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users = db.query(BotUser).filter(
                BotUser.last_interaction >= thirty_days_ago
            ).count()
            
            # Users who joined today
            today = datetime.utcnow().date()
            new_users_today = db.query(BotUser).filter(
                BotUser.first_interaction >= datetime.combine(today, datetime.min.time())
            ).count()
            
            # Total commands executed
            total_commands = db.query(func.sum(BotUser.total_commands)).scalar() or 0
            
            # Top users by command usage (limit to top 5)
            top_users = db.query(BotUser).order_by(
                BotUser.total_commands.desc()
            ).limit(5).all()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'new_users_today': new_users_today,
                'total_commands': total_commands,
                'top_users': [
                    {
                        'user_id': user.user_id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'commands': user.total_commands,
                        'last_seen': user.last_interaction
                    }
                    for user in top_users
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'new_users_today': 0,
                'total_commands': 0,
                'top_users': []
            }
        finally:
            if db:
                db.close()
    
    async def get_user_details(self, user_id: str) -> Optional[Dict]:
        """
        Get details for a specific user
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            User details dictionary or None if not found
        """
        try:
            db = SessionLocal()
            
            user = db.query(BotUser).filter(BotUser.user_id == user_id).first()
            
            if user:
                result = {
                    'user_id': user.user_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'first_interaction': user.first_interaction,
                    'last_interaction': user.last_interaction,
                    'total_commands': user.total_commands,
                    'is_active': user.is_active
                }
                db.close()
                return result
            
            db.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting user details for {user_id}: {e}")
            return None
    
    def format_user_stats(self, stats: Dict) -> str:
        """Format user statistics into a readable message"""
        try:
            message = f"""
📊 **Bot User Statistics**

👥 **Total Users:** {stats['total_users']:,}
🟢 **Active Users (30 days):** {stats['active_users']:,}
🆕 **New Users Today:** {stats['new_users_today']:,}
⚡ **Total Commands:** {stats['total_commands']:,}

🏆 **Top Users by Activity:**
"""
            
            if stats['top_users']:
                for i, user in enumerate(stats['top_users'], 1):
                    name = user['first_name'] or user['username'] or f"User {user['user_id']}"
                    commands = user['commands']
                    last_seen = user['last_seen'].strftime("%Y-%m-%d")
                    message += f"{i}. {name} - {commands:,} commands (last: {last_seen})\n"
            else:
                message += "No user data available\n"
            
            message += f"\n🕐 Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting user stats: {e}")
            return "❌ Error generating user statistics"
    
    def is_admin_user(self, user_id: str) -> bool:
        """
        Check if user is an admin (authorized to view user statistics)
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            True if user is authorized admin
        """
        # Authorized admin user IDs
        admin_users = ['6344425256', '6361005920']
        return user_id in admin_users