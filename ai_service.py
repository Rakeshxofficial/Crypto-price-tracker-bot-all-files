"""
AI Service for crypto market analysis using OpenAI GPT-4
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from openai import OpenAI
from database import SessionLocal, AIAnalysis

logger = logging.getLogger(__name__)

class AIMarketAnalyst:
    """AI-powered crypto market analyst using OpenAI GPT-4"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        logger.info("AI Market Analyst initialized")
    
    async def should_i_buy_analysis(self, coin_data: Dict) -> str:
        """
        Generate AI-powered buy/sell advice for a cryptocurrency
        
        Args:
            coin_data: Dictionary containing coin info, price, volume, etc.
        
        Returns:
            AI analysis as string
        """
        try:
            # Check cache first
            cached_analysis = self._get_cached_analysis(coin_data['coin_id'], 'shouldibuy')
            if cached_analysis:
                return cached_analysis
            
            # Prepare the prompt
            prompt = self._build_shouldibuy_prompt(coin_data)
            
            # Get AI response
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Latest OpenAI model
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional cryptocurrency trading analyst. Provide concise, actionable trading advice based on technical and market data. Be direct and mention specific reasons for your recommendation."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_analysis = response.choices[0].message.content.strip()
            
            # Cache the result
            self._cache_analysis(coin_data['coin_id'], 'shouldibuy', prompt, ai_analysis)
            
            return ai_analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return "⚠️ AI analysis temporarily unavailable. Please try again later."
    
    def _build_shouldibuy_prompt(self, coin_data: Dict) -> str:
        """Build the prompt for should-I-buy analysis"""
        
        coin_name = coin_data.get('name', 'Unknown')
        coin_symbol = coin_data.get('symbol', '').upper()
        current_price = coin_data.get('current_price', 0)
        price_change_24h = coin_data.get('price_change_percentage_24h', 0)
        volume_24h = coin_data.get('total_volume', 0)
        market_cap = coin_data.get('market_cap', 0)
        market_cap_rank = coin_data.get('market_cap_rank', 'Unknown')
        
        # Determine volume level
        volume_level = "Low"
        if volume_24h > 1000000000:  # >1B
            volume_level = "Very High"
        elif volume_24h > 100000000:  # >100M
            volume_level = "High"
        elif volume_24h > 10000000:   # >10M
            volume_level = "Moderate"
        
        # Determine sentiment based on price change
        sentiment = "Neutral"
        if price_change_24h > 5:
            sentiment = "Very Bullish"
        elif price_change_24h > 2:
            sentiment = "Bullish"
        elif price_change_24h < -5:
            sentiment = "Very Bearish"
        elif price_change_24h < -2:
            sentiment = "Bearish"
        
        prompt = f"""
Act as a crypto trading assistant. Analyze this coin and provide buy/sell advice:

Coin: {coin_name} ({coin_symbol})
Current Price: ${current_price:,.4f}
24h Change: {price_change_24h:+.2f}%
24h Volume: ${volume_24h:,.0f} ({volume_level})
Market Cap Rank: #{market_cap_rank}
Market Sentiment: {sentiment}

Should I buy this coin now or wait? Consider:
- Current momentum and price action
- Volume trends
- Market position
- Risk factors

Provide a clear recommendation with reasoning in 2-3 sentences.
"""
        
        return prompt.strip()
    
    async def generate_daily_summary(self, top_coins: list) -> str:
        """Generate daily market summary"""
        try:
            # Check cache
            cached_summary = self._get_cached_analysis('market', 'daily_summary')
            if cached_summary:
                return cached_summary
            
            # Build market data
            market_data = []
            for coin in top_coins[:10]:  # Top 10 coins
                market_data.append({
                    'name': coin.get('name', ''),
                    'symbol': coin.get('symbol', '').upper(),
                    'price': coin.get('current_price', 0),
                    'change': coin.get('price_change_percentage_24h', 0)
                })
            
            prompt = f"""
Generate a concise daily crypto market digest based on this data:

{json.dumps(market_data, indent=2)}

Provide:
1. Overall market sentiment (1 line)
2. Top 3 gainers with percentages
3. Top 3 losers with percentages  
4. One key market insight or trend

Keep it under 200 words and engaging for crypto traders.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a crypto market analyst creating daily summaries for traders. Be informative and engaging."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=250,
                temperature=0.6
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Cache for 4 hours
            self._cache_analysis('market', 'daily_summary', prompt, summary, hours=4)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return "📊 Daily market summary temporarily unavailable."
    
    def _get_cached_analysis(self, coin_id: str, analysis_type: str) -> Optional[str]:
        """Get cached analysis if available and not expired"""
        try:
            db = SessionLocal()
            analysis = db.query(AIAnalysis).filter(
                AIAnalysis.coin_id == coin_id,
                AIAnalysis.analysis_type == analysis_type,
                AIAnalysis.expires_at > datetime.utcnow()
            ).first()
            
            if analysis:
                logger.info(f"Using cached {analysis_type} for {coin_id}")
                return analysis.ai_response
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached analysis: {e}")
            return None
        finally:
            db.close()
    
    def _cache_analysis(self, coin_id: str, analysis_type: str, prompt_data: str, 
                       ai_response: str, hours: int = 1):
        """Cache analysis result"""
        try:
            db = SessionLocal()
            
            # Remove old cache entries for this coin/type
            db.query(AIAnalysis).filter(
                AIAnalysis.coin_id == coin_id,
                AIAnalysis.analysis_type == analysis_type
            ).delete()
            
            # Add new cache entry
            expires_at = datetime.utcnow() + timedelta(hours=hours)
            cache_entry = AIAnalysis(
                coin_id=coin_id,
                analysis_type=analysis_type,
                prompt_data=prompt_data,
                ai_response=ai_response,
                expires_at=expires_at
            )
            
            db.add(cache_entry)
            db.commit()
            
            logger.info(f"Cached {analysis_type} analysis for {coin_id}")
            
        except Exception as e:
            logger.error(f"Error caching analysis: {e}")
        finally:
            db.close()