"""
AI-powered token risk assessment using OpenAI
"""
import os
import json
import logging
from typing import Dict, Optional
from openai import OpenAI
from token_scanner import TokenData

logger = logging.getLogger(__name__)

class TokenRiskAnalyzer:
    """AI-powered risk analysis for tokens using OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        logger.info("TokenRiskAnalyzer initialized")
    
    async def analyze_token_risk(self, token_data: TokenData) -> Dict[str, str]:
        """
        Analyze token risk using AI
        
        Args:
            token_data: TokenData object with comprehensive token information
            
        Returns:
            Dictionary with risk_level and explanation
        """
        try:
            prompt = self._build_risk_analysis_prompt(token_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using latest OpenAI model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cryptocurrency risk analyst. Analyze token data and provide risk assessment with clear, concise explanations. Always respond in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate response structure
            if 'risk_level' not in result or 'explanation' not in result:
                logger.error("Invalid AI response structure")
                return self._get_fallback_analysis(token_data)
            
            logger.info(f"AI risk analysis completed for {token_data.symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error in AI risk analysis: {e}")
            return self._get_fallback_analysis(token_data)
    
    def _build_risk_analysis_prompt(self, token_data: TokenData) -> str:
        """Build comprehensive prompt for AI risk analysis"""
        
        prompt = f"""Analyze this cryptocurrency token and assess its risk level:

Token Name: {token_data.name}
Symbol: {token_data.symbol}
Chain: {token_data.chain}
Price: ${token_data.price_usd:.8f}
Market Cap: ${token_data.market_cap:,.0f}
24h Volume: ${token_data.volume_24h:,.0f}
Liquidity: ${token_data.liquidity:,.0f}
Holders: {token_data.holders_count:,}
Top 10 Wallets Hold: {token_data.top_10_percent:.1f}%
Age: {token_data.age_days} days
Price Changes - 5m: {token_data.price_change_5m:.2f}%, 1h: {token_data.price_change_1h:.2f}%, 24h: {token_data.price_change_24h:.2f}%
Verified: {token_data.verified}
Honeypot Risk: {token_data.honeypot_risk}

Based on this data, assess the risk level and provide explanation. Consider:
- Concentration of top holders (high concentration = higher risk)
- Token age vs growth speed (very new + high growth = potential risk)
- Liquidity vs market cap ratio
- Extreme price movements
- Honeypot indicators

Respond with JSON containing:
- "risk_level": one of "🛑 HIGH RISK", "⚠️ MEDIUM RISK", or "✅ LOW RISK"
- "explanation": 1-2 concise sentences explaining the assessment

Example response:
{{"risk_level": "⚠️ MEDIUM RISK", "explanation": "High concentration with top 10 holders owning 65% of tokens. Young token age of 30 days requires caution despite decent liquidity."}}"""

        return prompt
    
    def _get_fallback_analysis(self, token_data: TokenData) -> Dict[str, str]:
        """Provide rule-based fallback analysis when AI fails"""
        
        risk_factors = []
        risk_score = 0
        
        # Analyze concentration risk with updated thresholds
        if token_data.top_10_percent > 80:
            risk_factors.append("extremely high holder concentration (>80%)")
            risk_score += 3
        elif token_data.top_10_percent > 50:
            risk_factors.append("high holder concentration (50-80%)")
            risk_score += 2
        elif token_data.top_10_percent > 30:
            risk_factors.append("moderate holder concentration (30-50%)")
            risk_score += 1
        
        # Analyze age risk
        if token_data.age_days < 1:
            risk_factors.append("very new token")
            risk_score += 3
        elif token_data.age_days < 7:
            risk_factors.append("new token")
            risk_score += 2
        elif token_data.age_days < 30:
            risk_factors.append("young token")
            risk_score += 1
        
        # Analyze liquidity risk
        if token_data.market_cap > 0 and token_data.liquidity > 0:
            liquidity_ratio = token_data.liquidity / token_data.market_cap
            if liquidity_ratio < 0.05:  # Less than 5% liquidity
                risk_factors.append("low liquidity")
                risk_score += 2
        
        # Analyze volatility risk
        if abs(token_data.price_change_1h) > 50:
            risk_factors.append("extreme volatility")
            risk_score += 2
        
        # Honeypot risk
        if token_data.honeypot_risk:
            risk_factors.append("honeypot indicators")
            risk_score += 3
        
        # Determine risk level
        if risk_score >= 6:
            risk_level = "🛑 HIGH RISK"
        elif risk_score >= 3:
            risk_level = "⚠️ MEDIUM RISK"
        else:
            risk_level = "✅ LOW RISK"
        
        # Build explanation
        if risk_factors:
            explanation = f"Risk factors detected: {', '.join(risk_factors[:2])}."
        else:
            explanation = "No major risk factors identified based on available data."
        
        return {
            "risk_level": risk_level,
            "explanation": explanation
        }