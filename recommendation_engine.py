"""
Personalized Crypto Investment Recommendation Engine
Analyzes user behavior, alerts, portfolio, and market data for tailored advice
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from database import SessionLocal, PriceAlert, UserWallet
from market_service import MarketService
from ai_service import AIMarketAnalyst
from portfolio_service import PortfolioService

logger = logging.getLogger(__name__)

class PersonalizedRecommendationEngine:
    """AI-powered personalized crypto investment recommendation engine"""
    
    def __init__(self):
        self.market_service = MarketService()
        self.ai_analyst = AIMarketAnalyst()
        self.portfolio_service = PortfolioService()
        logger.info("PersonalizedRecommendationEngine initialized")
    
    async def generate_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        Generate personalized investment recommendations based on user profile
        
        Args:
            user_id: User's Telegram ID
            
        Returns:
            Dictionary containing personalized recommendations
        """
        try:
            # Gather user data
            user_profile = await self._build_user_profile(user_id)
            
            # Get market insights
            market_data = await self._get_market_insights()
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(user_profile, market_data)
            
            return {
                "recommendations": recommendations,
                "user_risk_profile": user_profile.get("risk_level", "moderate"),
                "portfolio_analysis": user_profile.get("portfolio_analysis", {}),
                "market_sentiment": market_data.get("sentiment", "neutral"),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return {"error": "Unable to generate recommendations"}
    
    async def _build_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Build comprehensive user profile from historical data"""
        try:
            db = SessionLocal()
            
            # Get user's alert history
            alerts = db.query(PriceAlert).filter(
                PriceAlert.user_id == user_id
            ).all()
            
            # Get user's portfolio data
            default_wallet = db.query(UserWallet).filter(
                UserWallet.user_id == user_id,
                UserWallet.is_default == True,
                UserWallet.is_active == True
            ).first()
            
            portfolio_data = None
            if default_wallet:
                portfolio_data = await self.portfolio_service.get_wallet_portfolio(
                    default_wallet.wallet_address, 
                    default_wallet.blockchain
                )
            
            # Analyze user behavior patterns
            profile = {
                "alert_patterns": self._analyze_alert_patterns(alerts),
                "portfolio_analysis": self._analyze_portfolio(portfolio_data) if portfolio_data else {},
                "risk_level": self._determine_risk_level(alerts, portfolio_data),
                "preferred_coins": self._get_preferred_coins(alerts, portfolio_data),
                "investment_style": self._determine_investment_style(alerts, portfolio_data)
            }
            
            db.close()
            return profile
            
        except Exception as e:
            logger.error(f"Error building user profile: {e}")
            return {}
    
    def _analyze_alert_patterns(self, alerts: List) -> Dict[str, Any]:
        """Analyze user's alert setting patterns"""
        if not alerts:
            return {"total_alerts": 0, "avg_target_variance": 0}
        
        total_alerts = len(alerts)
        above_alerts = sum(1 for alert in alerts if alert.is_above)
        below_alerts = total_alerts - above_alerts
        
        # Calculate average target price variance (risk indicator)
        recent_alerts = [a for a in alerts if a.created_at > datetime.utcnow() - timedelta(days=30)]
        
        return {
            "total_alerts": total_alerts,
            "above_alerts": above_alerts,
            "below_alerts": below_alerts,
            "alert_ratio": above_alerts / total_alerts if total_alerts > 0 else 0,
            "recent_activity": len(recent_alerts),
            "most_watched_coins": self._get_most_watched_coins(alerts)
        }
    
    def _analyze_portfolio(self, portfolio_data: Optional[Dict]) -> Dict[str, Any]:
        """Analyze user's current portfolio composition"""
        if not portfolio_data or not portfolio_data.get("tokens"):
            return {"diversification": "unknown", "total_value": 0}
        
        tokens = portfolio_data["tokens"]
        total_value = portfolio_data.get("total_value_usd", 0)
        
        # Calculate diversification metrics
        num_tokens = len(tokens)
        
        # Categorize tokens by market cap (assuming we have this data)
        large_cap = medium_cap = small_cap = 0
        for token in tokens:
            value = token.get("value_usd", 0)
            if value > 1000:  # Large holdings
                large_cap += 1
            elif value > 100:  # Medium holdings
                medium_cap += 1
            else:  # Small holdings
                small_cap += 1
        
        return {
            "total_value": total_value,
            "num_tokens": num_tokens,
            "diversification": "high" if num_tokens > 10 else "medium" if num_tokens > 5 else "low",
            "large_cap_holdings": large_cap,
            "medium_cap_holdings": medium_cap,
            "small_cap_holdings": small_cap,
            "top_holdings": [token["symbol"] for token in tokens[:3]]
        }
    
    def _determine_risk_level(self, alerts: List, portfolio_data: Optional[Dict]) -> str:
        """Determine user's risk tolerance based on behavior"""
        risk_score = 0
        
        # Portfolio analysis
        if portfolio_data and portfolio_data.get("tokens"):
            num_tokens = len(portfolio_data["tokens"])
            if num_tokens > 15:  # Highly diversified
                risk_score += 1
            elif num_tokens < 5:  # Concentrated
                risk_score += 3
            else:
                risk_score += 2
        
        # Alert patterns
        if alerts:
            above_ratio = sum(1 for a in alerts if a.is_above) / len(alerts)
            if above_ratio > 0.7:  # Mostly buying alerts
                risk_score += 2
            elif above_ratio < 0.3:  # Mostly selling alerts
                risk_score += 1
        
        # Determine risk level
        if risk_score <= 2:
            return "conservative"
        elif risk_score <= 4:
            return "moderate"
        else:
            return "aggressive"
    
    def _get_preferred_coins(self, alerts: List, portfolio_data: Optional[Dict]) -> List[str]:
        """Identify user's preferred cryptocurrencies"""
        coin_frequency = {}
        
        # From alerts
        for alert in alerts:
            coin = alert.coin_symbol
            coin_frequency[coin] = coin_frequency.get(coin, 0) + 1
        
        # From portfolio
        if portfolio_data and portfolio_data.get("tokens"):
            for token in portfolio_data["tokens"]:
                symbol = token.get("symbol", "")
                if symbol:
                    coin_frequency[symbol] = coin_frequency.get(symbol, 0) + 2  # Weight portfolio higher
        
        # Return top 5 preferred coins
        return sorted(coin_frequency.keys(), key=lambda x: coin_frequency[x], reverse=True)[:5]
    
    def _determine_investment_style(self, alerts: List, portfolio_data: Optional[Dict]) -> str:
        """Determine user's investment style"""
        if not alerts and not portfolio_data:
            return "beginner"
        
        # Analyze alert frequency
        if alerts:
            recent_alerts = [a for a in alerts if a.created_at > datetime.utcnow() - timedelta(days=7)]
            if len(recent_alerts) > 10:
                return "active_trader"
            elif len(alerts) > 20:
                return "regular_trader"
        
        # Analyze portfolio size
        if portfolio_data:
            total_value = portfolio_data.get("total_value_usd", 0)
            if total_value > 10000:
                return "serious_investor"
            elif total_value > 1000:
                return "casual_investor"
        
        return "moderate_trader"
    
    def _get_most_watched_coins(self, alerts: List) -> List[str]:
        """Get most frequently alerted coins"""
        coin_count = {}
        for alert in alerts:
            coin = alert.coin_symbol
            coin_count[coin] = coin_count.get(coin, 0) + 1
        
        return sorted(coin_count.keys(), key=lambda x: coin_count[x], reverse=True)[:5]
    
    async def _get_market_insights(self) -> Dict[str, Any]:
        """Get current market insights and trends"""
        try:
            # Get trending coins
            trending = await self.market_service.get_trending_coins()
            
            # Get top market cap coins
            top_coins = await self.market_service.get_top_coins_by_market_cap(10)
            
            # Calculate market sentiment
            sentiment = await self._calculate_market_sentiment(top_coins)
            
            return {
                "trending_coins": [coin.get("symbol", "") for coin in (trending or [])[:5]],
                "top_gainers": await self._get_top_gainers(top_coins),
                "sentiment": sentiment,
                "market_cap_leaders": [coin.get("symbol", "") for coin in (top_coins or [])[:5]]
            }
            
        except Exception as e:
            logger.error(f"Error getting market insights: {e}")
            return {"sentiment": "neutral"}
    
    async def _calculate_market_sentiment(self, top_coins: Optional[List]) -> str:
        """Calculate overall market sentiment"""
        if not top_coins:
            return "neutral"
        
        positive_count = 0
        total_count = 0
        
        for coin in top_coins:
            change_24h = coin.get("price_change_percentage_24h", 0)
            if change_24h > 0:
                positive_count += 1
            total_count += 1
        
        if total_count == 0:
            return "neutral"
        
        positive_ratio = positive_count / total_count
        
        if positive_ratio > 0.7:
            return "bullish"
        elif positive_ratio < 0.3:
            return "bearish"
        else:
            return "neutral"
    
    async def _get_top_gainers(self, top_coins: Optional[List]) -> List[str]:
        """Get top gaining coins from market data"""
        if not top_coins:
            return []
        
        # Sort by 24h price change
        sorted_coins = sorted(
            top_coins, 
            key=lambda x: x.get("price_change_percentage_24h", 0), 
            reverse=True
        )
        
        return [coin.get("symbol", "") for coin in sorted_coins[:3]]
    
    async def _generate_recommendations(self, user_profile: Dict, market_data: Dict) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on user profile and market data"""
        recommendations = []
        
        try:
            risk_level = user_profile.get("risk_level", "moderate")
            investment_style = user_profile.get("investment_style", "moderate_trader")
            preferred_coins = user_profile.get("preferred_coins", [])
            
            # Recommendation 1: Portfolio Diversification
            if user_profile.get("portfolio_analysis", {}).get("diversification") == "low":
                recommendations.append({
                    "type": "diversification",
                    "title": "🌐 Diversify Your Portfolio",
                    "description": f"Consider adding more assets to reduce risk. Your portfolio has {user_profile.get('portfolio_analysis', {}).get('num_tokens', 0)} tokens.",
                    "suggested_coins": market_data.get("market_cap_leaders", [])[:3],
                    "priority": "high",
                    "reasoning": "Low diversification increases portfolio risk"
                })
            
            # Recommendation 2: Trending Opportunities
            trending_coins = market_data.get("trending_coins", [])
            if trending_coins and risk_level in ["moderate", "aggressive"]:
                recommendations.append({
                    "type": "trending",
                    "title": "🔥 Trending Opportunities",
                    "description": "These coins are gaining attention in the market",
                    "suggested_coins": trending_coins[:3],
                    "priority": "medium",
                    "reasoning": "Based on current market trends and your risk profile"
                })
            
            # Recommendation 3: Risk-based suggestions
            if risk_level == "conservative":
                recommendations.append({
                    "type": "conservative",
                    "title": "🛡️ Safe Haven Assets",
                    "description": "Consider established cryptocurrencies with lower volatility",
                    "suggested_coins": ["BTC", "ETH"],
                    "priority": "high",
                    "reasoning": "Matches your conservative risk profile"
                })
            elif risk_level == "aggressive":
                recommendations.append({
                    "type": "aggressive",
                    "title": "🚀 High Growth Potential",
                    "description": "Explore emerging altcoins with high growth potential",
                    "suggested_coins": market_data.get("top_gainers", []),
                    "priority": "medium",
                    "reasoning": "Aligns with your aggressive investment style"
                })
            
            # Recommendation 4: Based on user's alert patterns
            most_watched = user_profile.get("alert_patterns", {}).get("most_watched_coins", [])
            if most_watched:
                recommendations.append({
                    "type": "watchlist",
                    "title": "👀 Your Watchlist Insights",
                    "description": f"You frequently monitor {', '.join(most_watched[:3])}. Consider AI analysis for timing.",
                    "suggested_coins": most_watched[:3],
                    "priority": "medium",
                    "reasoning": "Based on your frequent price monitoring"
                })
            
            # Recommendation 5: Market sentiment based
            sentiment = market_data.get("sentiment", "neutral")
            if sentiment == "bullish":
                recommendations.append({
                    "type": "market_sentiment",
                    "title": "📈 Market Momentum",
                    "description": "Current market sentiment is bullish. Consider gradual position building.",
                    "suggested_coins": market_data.get("top_gainers", [])[:2],
                    "priority": "low",
                    "reasoning": "Positive market sentiment detected"
                })
            elif sentiment == "bearish":
                recommendations.append({
                    "type": "market_sentiment",
                    "title": "🔒 Defensive Strategy",
                    "description": "Market shows bearish signals. Focus on stable assets and DCA strategy.",
                    "suggested_coins": ["BTC", "ETH", "USDC"],
                    "priority": "high",
                    "reasoning": "Bearish market conditions require defensive approach"
                })
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def get_coin_specific_recommendation(self, user_id: str, coin_id: str) -> Dict[str, Any]:
        """Get personalized recommendation for a specific coin"""
        try:
            user_profile = await self._build_user_profile(user_id)
            coin_data = await self.market_service.get_detailed_coin_data(coin_id)
            
            if not coin_data:
                return {"error": "Unable to fetch coin data"}
            
            # Get AI analysis
            ai_analysis = await self.ai_analyst.should_i_buy_analysis(coin_data)
            
            # Personalize based on user profile
            risk_level = user_profile.get("risk_level", "moderate")
            investment_style = user_profile.get("investment_style", "moderate_trader")
            
            # Adjust recommendation based on user profile
            personalized_advice = self._personalize_coin_advice(
                ai_analysis, risk_level, investment_style, coin_data
            )
            
            return {
                "coin_symbol": coin_data.get("symbol", "").upper(),
                "coin_name": coin_data.get("name", ""),
                "current_price": coin_data.get("current_price", 0),
                "ai_analysis": ai_analysis,
                "personalized_advice": personalized_advice,
                "user_risk_level": risk_level,
                "investment_style": investment_style
            }
            
        except Exception as e:
            logger.error(f"Error getting coin recommendation: {e}")
            return {"error": "Unable to generate recommendation"}
    
    def _personalize_coin_advice(self, ai_analysis: str, risk_level: str, investment_style: str, coin_data: Dict) -> str:
        """Personalize AI advice based on user profile"""
        try:
            price_change_24h = coin_data.get("price_change_percentage_24h", 0)
            market_cap_rank = coin_data.get("market_cap_rank", 999)
            
            advice = f"\n🎯 **Personalized for {risk_level.title()} {investment_style.replace('_', ' ').title()}:**\n"
            
            if risk_level == "conservative":
                if market_cap_rank <= 10:
                    advice += "✅ This established coin fits your conservative approach.\n"
                else:
                    advice += "⚠️ Consider larger market cap alternatives for your risk profile.\n"
                
                if abs(price_change_24h) > 10:
                    advice += "📊 High volatility detected. Consider DCA strategy.\n"
                
            elif risk_level == "aggressive":
                if price_change_24h > 5:
                    advice += "🚀 Strong momentum aligns with your aggressive style.\n"
                elif price_change_24h < -5:
                    advice += "💎 Potential buying opportunity for risk-tolerant investors.\n"
                
            else:  # moderate
                advice += "⚖️ Balanced approach recommended for moderate risk tolerance.\n"
            
            # Investment style specific advice
            if "trader" in investment_style:
                advice += "📈 Monitor short-term trends and set alerts for entry/exit points.\n"
            elif "investor" in investment_style:
                advice += "🏗️ Focus on fundamentals and long-term growth potential.\n"
            
            return advice
            
        except Exception as e:
            logger.error(f"Error personalizing advice: {e}")
            return "Use standard analysis above for guidance."
    
    async def close(self):
        """Close connections"""
        await self.market_service.close()