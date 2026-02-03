# aria_skills/market_data.py
"""
📈 Market Data Skill - Crypto Trader Focus

Provides market data analysis for Aria's Crypto Trader persona.
Handles price feeds, technical indicators, and market sentiment.
"""
import json
import os
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from .base import BaseSkill, SkillConfig, SkillResult, SkillStatus


@dataclass
class OHLCV:
    """Price candle data."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class MarketTicker:
    """Market ticker data."""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    market_cap: Optional[float] = None
    timestamp: datetime = None


class MarketDataSkill(BaseSkill):
    """
    Cryptocurrency market data and analysis.
    
    Capabilities:
    - Price data fetching
    - Technical indicator calculation
    - Market sentiment analysis
    - Alert monitoring
    
    Note: This is a simulation for development.
    Production would integrate with real APIs (CoinGecko, Binance, etc.)
    """
    
    # Simulated market data for common pairs
    MOCK_PRICES = {
        "BTC/USDT": 67500.0,
        "ETH/USDT": 3850.0,
        "SOL/USDT": 175.0,
        "AVAX/USDT": 42.0,
        "LINK/USDT": 18.5,
        "DOT/USDT": 8.2,
    }
    
    @property
    def name(self) -> str:
        return "market_data"
    
    async def initialize(self) -> bool:
        """Initialize market data skill."""
        self._alerts: list[dict] = []
        self._status = SkillStatus.AVAILABLE
        self.logger.info("📈 Market data skill initialized")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check market data availability."""
        return self._status
    
    async def get_price(self, symbol: str) -> SkillResult:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            
        Returns:
            SkillResult with price data
        """
        try:
            symbol = symbol.upper()
            
            if symbol in self.MOCK_PRICES:
                base_price = self.MOCK_PRICES[symbol]
                # Add some variance
                price = base_price * (1 + random.uniform(-0.02, 0.02))
                change = random.uniform(-5, 5)
                
                return SkillResult.ok({
                    "symbol": symbol,
                    "price": round(price, 2),
                    "change_24h": round(change, 2),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return SkillResult.fail(f"Unknown symbol: {symbol}")
                
        except Exception as e:
            return SkillResult.fail(f"Price fetch failed: {str(e)}")
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 24
    ) -> SkillResult:
        """
        Get OHLCV (candlestick) data.
        
        Args:
            symbol: Trading pair
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles
            
        Returns:
            SkillResult with OHLCV data
        """
        try:
            symbol = symbol.upper()
            if symbol not in self.MOCK_PRICES:
                return SkillResult.fail(f"Unknown symbol: {symbol}")
            
            base_price = self.MOCK_PRICES[symbol]
            candles = []
            
            # Generate mock candles
            timeframe_minutes = {
                "1m": 1, "5m": 5, "15m": 15,
                "1h": 60, "4h": 240, "1d": 1440
            }.get(timeframe, 60)
            
            current_price = base_price
            now = datetime.utcnow()
            
            for i in range(limit - 1, -1, -1):
                timestamp = now - timedelta(minutes=timeframe_minutes * i)
                
                # Random walk
                change = random.uniform(-0.02, 0.02)
                open_price = current_price
                close_price = open_price * (1 + change)
                high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
                low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
                volume = base_price * random.uniform(100, 1000)
                
                candles.append({
                    "timestamp": timestamp.isoformat(),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": round(volume, 2)
                })
                
                current_price = close_price
            
            return SkillResult.ok({
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": candles,
                "count": len(candles)
            })
            
        except Exception as e:
            return SkillResult.fail(f"OHLCV fetch failed: {str(e)}")
    
    async def calculate_indicators(
        self,
        symbol: str,
        indicators: list[str],
        timeframe: str = "1h"
    ) -> SkillResult:
        """
        Calculate technical indicators.
        
        Args:
            symbol: Trading pair
            indicators: List of indicators (sma, ema, rsi, macd, bollinger)
            timeframe: Data timeframe
            
        Returns:
            SkillResult with indicator values
        """
        try:
            # Get OHLCV data
            ohlcv_result = await self.get_ohlcv(symbol, timeframe, limit=50)
            if not ohlcv_result.success:
                return ohlcv_result
            
            candles = ohlcv_result.data["candles"]
            closes = [c["close"] for c in candles]
            
            results = {}
            
            for indicator in indicators:
                indicator = indicator.lower()
                
                if indicator == "sma" or indicator == "sma_20":
                    results["sma_20"] = round(sum(closes[-20:]) / 20, 2)
                
                elif indicator == "ema" or indicator == "ema_12":
                    results["ema_12"] = round(self._calculate_ema(closes, 12), 2)
                
                elif indicator == "rsi":
                    results["rsi_14"] = round(self._calculate_rsi(closes, 14), 2)
                
                elif indicator == "macd":
                    ema_12 = self._calculate_ema(closes, 12)
                    ema_26 = self._calculate_ema(closes, 26)
                    macd_line = ema_12 - ema_26
                    results["macd"] = {
                        "macd_line": round(macd_line, 2),
                        "signal": round(macd_line * 0.9, 2),  # Simplified
                        "histogram": round(macd_line * 0.1, 2)
                    }
                
                elif indicator == "bollinger":
                    sma = sum(closes[-20:]) / 20
                    std = (sum((c - sma) ** 2 for c in closes[-20:]) / 20) ** 0.5
                    results["bollinger"] = {
                        "middle": round(sma, 2),
                        "upper": round(sma + 2 * std, 2),
                        "lower": round(sma - 2 * std, 2)
                    }
            
            return SkillResult.ok({
                "symbol": symbol,
                "timeframe": timeframe,
                "indicators": results,
                "calculated_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Indicator calculation failed: {str(e)}")
    
    async def analyze_sentiment(self, symbol: str) -> SkillResult:
        """
        Analyze market sentiment for a symbol.
        
        Args:
            symbol: Trading pair
            
        Returns:
            SkillResult with sentiment analysis
        """
        try:
            # Mock sentiment analysis
            fear_greed = random.randint(20, 80)
            
            sentiment = "neutral"
            if fear_greed < 30:
                sentiment = "extreme_fear"
            elif fear_greed < 45:
                sentiment = "fear"
            elif fear_greed > 70:
                sentiment = "extreme_greed"
            elif fear_greed > 55:
                sentiment = "greed"
            
            return SkillResult.ok({
                "symbol": symbol.upper(),
                "fear_greed_index": fear_greed,
                "sentiment": sentiment,
                "social_volume": random.randint(1000, 50000),
                "social_sentiment": random.choice(["bullish", "bearish", "neutral"]),
                "whale_activity": random.choice(["low", "medium", "high"]),
                "analyzed_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Sentiment analysis failed: {str(e)}")
    
    async def set_alert(
        self,
        symbol: str,
        condition: str,
        value: float
    ) -> SkillResult:
        """
        Set a price alert.
        
        Args:
            symbol: Trading pair
            condition: Alert condition (above, below, cross)
            value: Target price
            
        Returns:
            SkillResult confirming alert
        """
        try:
            alert = {
                "id": len(self._alerts) + 1,
                "symbol": symbol.upper(),
                "condition": condition,
                "value": value,
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
            
            self._alerts.append(alert)
            
            return SkillResult.ok({
                "alert_id": alert["id"],
                "message": f"Alert set: {symbol} {condition} {value}",
                "alert": alert
            })
            
        except Exception as e:
            return SkillResult.fail(f"Alert creation failed: {str(e)}")
    
    async def check_alerts(self) -> SkillResult:
        """
        Check all active alerts against current prices.
        
        Returns:
            SkillResult with triggered alerts
        """
        try:
            triggered = []
            
            for alert in self._alerts:
                if alert["status"] != "active":
                    continue
                
                symbol = alert["symbol"]
                if symbol not in self.MOCK_PRICES:
                    continue
                
                current_price = self.MOCK_PRICES[symbol] * (1 + random.uniform(-0.02, 0.02))
                
                is_triggered = False
                if alert["condition"] == "above" and current_price > alert["value"]:
                    is_triggered = True
                elif alert["condition"] == "below" and current_price < alert["value"]:
                    is_triggered = True
                
                if is_triggered:
                    alert["status"] = "triggered"
                    alert["triggered_at"] = datetime.utcnow().isoformat()
                    alert["triggered_price"] = round(current_price, 2)
                    triggered.append(alert)
            
            return SkillResult.ok({
                "triggered": triggered,
                "triggered_count": len(triggered),
                "active_alerts": len([a for a in self._alerts if a["status"] == "active"]),
                "checked_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Alert check failed: {str(e)}")
    
    async def get_market_overview(self) -> SkillResult:
        """
        Get overall market overview.
        
        Returns:
            SkillResult with market summary
        """
        try:
            tickers = []
            total_market_cap = 0
            
            for symbol, base_price in self.MOCK_PRICES.items():
                price = base_price * (1 + random.uniform(-0.02, 0.02))
                change = random.uniform(-5, 5)
                volume = base_price * random.uniform(1e6, 1e8)
                market_cap = base_price * random.uniform(1e9, 1e12)
                
                tickers.append({
                    "symbol": symbol,
                    "price": round(price, 2),
                    "change_24h": round(change, 2),
                    "volume_24h": round(volume, 0),
                    "market_cap": round(market_cap, 0)
                })
                
                total_market_cap += market_cap
            
            # Sort by market cap
            tickers.sort(key=lambda x: x["market_cap"], reverse=True)
            
            return SkillResult.ok({
                "tickers": tickers,
                "total_market_cap": round(total_market_cap, 0),
                "btc_dominance": round(random.uniform(40, 55), 1),
                "market_trend": random.choice(["bullish", "bearish", "sideways"]),
                "updated_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Market overview failed: {str(e)}")
    
    # === Private Helper Methods ===
    
    def _calculate_ema(self, prices: list[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period  # Start with SMA
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_rsi(self, prices: list[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50  # Neutral
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [c if c > 0 else 0 for c in changes[-period:]]
        losses = [-c if c < 0 else 0 for c in changes[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi


# Skill instance factory
def create_skill(config: SkillConfig) -> MarketDataSkill:
    """Create a market data skill instance."""
    return MarketDataSkill(config)
