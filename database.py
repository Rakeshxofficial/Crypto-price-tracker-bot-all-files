"""
Database models and setup for the AI Crypto Assistant Bot
"""

import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PriceAlert(Base):
    """Model for storing user price alerts"""
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    coin_id = Column(String, nullable=False)
    coin_symbol = Column(String, nullable=False)
    target_price = Column(Float, nullable=False)
    is_above = Column(Boolean, default=True)  # True for "alert when above", False for "alert when below"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)

class UserWallet(Base):
    """Model for storing user wallet addresses for tracking"""
    __tablename__ = "user_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    wallet_address = Column(String, nullable=False)
    blockchain = Column(String, nullable=False)  # eth, bsc, polygon, etc.
    label = Column(String, nullable=True)  # optional user label
    is_default = Column(Boolean, default=False)  # default wallet for user
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class AIAnalysis(Base):
    """Model for caching AI analysis results"""
    __tablename__ = "ai_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)  # "shouldibuy", "daily_summary", etc.
    prompt_data = Column(Text, nullable=False)  # JSON string of the data used
    ai_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # Cache expiry

class UserWalletKeys(Base):
    """Model for storing encrypted user wallet keys"""
    __tablename__ = "user_wallet_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, nullable=False, index=True)
    encrypted_mnemonic = Column(Text, nullable=False)
    eth_address = Column(String, nullable=False)
    solana_address = Column(String, nullable=False)
    tron_address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class BotUser(Base):
    """Model for tracking bot users"""
    __tablename__ = "bot_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    first_interaction = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    total_commands = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

class LiveNotification(Base):
    """Model for live price notifications"""
    __tablename__ = "live_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    coin_id = Column(String, nullable=False)
    coin_symbol = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sent = Column(DateTime, nullable=True)

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database on startup"""
    create_tables()