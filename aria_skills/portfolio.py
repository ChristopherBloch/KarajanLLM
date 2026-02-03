# aria_skills/portfolio.py
"""
📈 Portfolio Management Skill - Crypto Trader Focus

Provides portfolio tracking and risk management for Aria's Trader persona.
Handles position tracking, P&L calculation, and risk metrics.
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .base import BaseSkill, SkillConfig, SkillResult, SkillStatus


@dataclass
class Position:
    """A portfolio position."""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    side: str = "long"  # long or short
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class Trade:
    """A completed trade record."""
    id: int
    symbol: str
    side: str
    quantity: float
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_percent: float


class PortfolioSkill(BaseSkill):
    """
    Portfolio and position management.
    
    Capabilities:
    - Position tracking
    - P&L calculation
    - Risk metrics (Sharpe, drawdown, etc.)
    - Trade journaling
    - Portfolio allocation
    """
    
    @property
    def name(self) -> str:
        return "portfolio"
    
    async def initialize(self) -> bool:
        """Initialize portfolio skill."""
        self._positions: dict[str, Position] = {}
        self._trades: list[Trade] = []
        self._balance = 10000.0  # Starting balance
        self._trade_counter = 0
        self._status = SkillStatus.AVAILABLE
        self.logger.info("💼 Portfolio skill initialized")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check portfolio skill availability."""
        return self._status
    
    async def open_position(
        self,
        symbol: str,
        quantity: float,
        price: float,
        side: str = "long",
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> SkillResult:
        """
        Open a new position.
        
        Args:
            symbol: Trading pair
            quantity: Position size
            price: Entry price
            side: long or short
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price
            
        Returns:
            SkillResult with position details
        """
        try:
            symbol = symbol.upper()
            
            if symbol in self._positions:
                return SkillResult.fail(f"Position already exists for {symbol}")
            
            cost = quantity * price
            if cost > self._balance:
                return SkillResult.fail(f"Insufficient balance. Need {cost}, have {self._balance}")
            
            position = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=price,
                entry_time=datetime.utcnow(),
                side=side,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            self._positions[symbol] = position
            self._balance -= cost
            
            return SkillResult.ok({
                "position": {
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "entry_price": price,
                    "cost": cost,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit
                },
                "remaining_balance": round(self._balance, 2),
                "opened_at": position.entry_time.isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Position open failed: {str(e)}")
    
    async def close_position(
        self,
        symbol: str,
        price: float,
        reason: str = "manual"
    ) -> SkillResult:
        """
        Close an existing position.
        
        Args:
            symbol: Trading pair
            price: Exit price
            reason: Reason for closing (manual, stop_loss, take_profit)
            
        Returns:
            SkillResult with trade summary
        """
        try:
            symbol = symbol.upper()
            
            if symbol not in self._positions:
                return SkillResult.fail(f"No position for {symbol}")
            
            position = self._positions[symbol]
            
            # Calculate P&L
            if position.side == "long":
                pnl = (price - position.entry_price) * position.quantity
            else:
                pnl = (position.entry_price - price) * position.quantity
            
            pnl_percent = (pnl / (position.entry_price * position.quantity)) * 100
            
            # Record trade
            self._trade_counter += 1
            trade = Trade(
                id=self._trade_counter,
                symbol=symbol,
                side=position.side,
                quantity=position.quantity,
                entry_price=position.entry_price,
                exit_price=price,
                entry_time=position.entry_time,
                exit_time=datetime.utcnow(),
                pnl=pnl,
                pnl_percent=pnl_percent
            )
            self._trades.append(trade)
            
            # Update balance
            proceeds = position.quantity * price
            self._balance += proceeds
            
            # Remove position
            del self._positions[symbol]
            
            return SkillResult.ok({
                "trade": {
                    "id": trade.id,
                    "symbol": symbol,
                    "side": trade.side,
                    "quantity": trade.quantity,
                    "entry_price": trade.entry_price,
                    "exit_price": trade.exit_price,
                    "pnl": round(trade.pnl, 2),
                    "pnl_percent": round(trade.pnl_percent, 2),
                    "reason": reason
                },
                "new_balance": round(self._balance, 2),
                "closed_at": trade.exit_time.isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Position close failed: {str(e)}")
    
    async def get_positions(self, current_prices: Optional[dict] = None) -> SkillResult:
        """
        Get all open positions with current values.
        
        Args:
            current_prices: Optional dict of symbol: price for P&L calculation
            
        Returns:
            SkillResult with positions and unrealized P&L
        """
        try:
            positions = []
            total_value = 0
            total_unrealized_pnl = 0
            
            for symbol, pos in self._positions.items():
                current_price = current_prices.get(symbol, pos.entry_price) if current_prices else pos.entry_price
                
                if pos.side == "long":
                    unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
                else:
                    unrealized_pnl = (pos.entry_price - current_price) * pos.quantity
                
                position_value = pos.quantity * current_price
                total_value += position_value
                total_unrealized_pnl += unrealized_pnl
                
                positions.append({
                    "symbol": symbol,
                    "side": pos.side,
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": current_price,
                    "position_value": round(position_value, 2),
                    "unrealized_pnl": round(unrealized_pnl, 2),
                    "pnl_percent": round((unrealized_pnl / (pos.entry_price * pos.quantity)) * 100, 2),
                    "stop_loss": pos.stop_loss,
                    "take_profit": pos.take_profit,
                    "entry_time": pos.entry_time.isoformat()
                })
            
            return SkillResult.ok({
                "positions": positions,
                "position_count": len(positions),
                "total_position_value": round(total_value, 2),
                "total_unrealized_pnl": round(total_unrealized_pnl, 2),
                "cash_balance": round(self._balance, 2),
                "total_portfolio_value": round(self._balance + total_value, 2)
            })
            
        except Exception as e:
            return SkillResult.fail(f"Position fetch failed: {str(e)}")
    
    async def get_trade_history(
        self,
        symbol: Optional[str] = None,
        limit: int = 50
    ) -> SkillResult:
        """
        Get trade history.
        
        Args:
            symbol: Optional filter by symbol
            limit: Maximum trades to return
            
        Returns:
            SkillResult with trade history
        """
        try:
            trades = self._trades
            
            if symbol:
                trades = [t for t in trades if t.symbol == symbol.upper()]
            
            # Most recent first
            trades = sorted(trades, key=lambda t: t.exit_time, reverse=True)[:limit]
            
            return SkillResult.ok({
                "trades": [
                    {
                        "id": t.id,
                        "symbol": t.symbol,
                        "side": t.side,
                        "quantity": t.quantity,
                        "entry_price": t.entry_price,
                        "exit_price": t.exit_price,
                        "pnl": round(t.pnl, 2),
                        "pnl_percent": round(t.pnl_percent, 2),
                        "entry_time": t.entry_time.isoformat(),
                        "exit_time": t.exit_time.isoformat()
                    }
                    for t in trades
                ],
                "trade_count": len(trades)
            })
            
        except Exception as e:
            return SkillResult.fail(f"Trade history fetch failed: {str(e)}")
    
    async def get_performance_metrics(self) -> SkillResult:
        """
        Calculate portfolio performance metrics.
        
        Returns:
            SkillResult with performance metrics
        """
        try:
            if not self._trades:
                return SkillResult.ok({
                    "message": "No trades to analyze",
                    "total_trades": 0
                })
            
            # Basic stats
            total_pnl = sum(t.pnl for t in self._trades)
            winning_trades = [t for t in self._trades if t.pnl > 0]
            losing_trades = [t for t in self._trades if t.pnl < 0]
            
            win_rate = len(winning_trades) / len(self._trades) * 100 if self._trades else 0
            
            avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
            avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
            
            # Profit factor
            gross_profit = sum(t.pnl for t in winning_trades)
            gross_loss = abs(sum(t.pnl for t in losing_trades))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # Max drawdown (simplified)
            equity_curve = [10000]  # Starting balance
            for trade in sorted(self._trades, key=lambda t: t.exit_time):
                equity_curve.append(equity_curve[-1] + trade.pnl)
            
            max_drawdown = 0
            peak = equity_curve[0]
            for equity in equity_curve:
                if equity > peak:
                    peak = equity
                drawdown = (peak - equity) / peak * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            # Risk/Reward ratio
            risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            
            return SkillResult.ok({
                "total_trades": len(self._trades),
                "winning_trades": len(winning_trades),
                "losing_trades": len(losing_trades),
                "win_rate": round(win_rate, 2),
                "total_pnl": round(total_pnl, 2),
                "average_win": round(avg_win, 2),
                "average_loss": round(avg_loss, 2),
                "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "∞",
                "risk_reward_ratio": round(risk_reward, 2) if risk_reward != float('inf') else "∞",
                "max_drawdown_percent": round(max_drawdown, 2),
                "current_balance": round(self._balance, 2),
                "roi_percent": round((self._balance - 10000) / 10000 * 100, 2)
            })
            
        except Exception as e:
            return SkillResult.fail(f"Metrics calculation failed: {str(e)}")
    
    async def get_allocation(self, current_prices: Optional[dict] = None) -> SkillResult:
        """
        Get portfolio allocation breakdown.
        
        Args:
            current_prices: Optional prices for value calculation
            
        Returns:
            SkillResult with allocation percentages
        """
        try:
            positions_result = await self.get_positions(current_prices)
            if not positions_result.success:
                return positions_result
            
            total_value = positions_result.data["total_portfolio_value"]
            allocations = []
            
            # Cash allocation
            cash_percent = (self._balance / total_value * 100) if total_value > 0 else 100
            allocations.append({
                "asset": "CASH",
                "value": round(self._balance, 2),
                "percent": round(cash_percent, 2)
            })
            
            # Position allocations
            for pos in positions_result.data["positions"]:
                percent = (pos["position_value"] / total_value * 100) if total_value > 0 else 0
                allocations.append({
                    "asset": pos["symbol"],
                    "value": pos["position_value"],
                    "percent": round(percent, 2)
                })
            
            return SkillResult.ok({
                "allocations": allocations,
                "total_value": round(total_value, 2),
                "diversification_score": self._calculate_diversification(allocations)
            })
            
        except Exception as e:
            return SkillResult.fail(f"Allocation calculation failed: {str(e)}")
    
    async def check_risk_limits(
        self,
        max_position_size: float = 0.2,
        max_drawdown: float = 0.1
    ) -> SkillResult:
        """
        Check if portfolio respects risk limits.
        
        Args:
            max_position_size: Maximum position as % of portfolio (0.2 = 20%)
            max_drawdown: Maximum acceptable drawdown (0.1 = 10%)
            
        Returns:
            SkillResult with risk check results
        """
        try:
            violations = []
            warnings = []
            
            # Get current allocation
            allocation_result = await self.get_allocation()
            if not allocation_result.success:
                return allocation_result
            
            total_value = allocation_result.data["total_value"]
            
            # Check position sizes
            for alloc in allocation_result.data["allocations"]:
                if alloc["asset"] != "CASH":
                    if alloc["percent"] > max_position_size * 100:
                        violations.append(f"{alloc['asset']} exceeds max position size: {alloc['percent']}% > {max_position_size*100}%")
            
            # Check drawdown
            metrics_result = await self.get_performance_metrics()
            if metrics_result.success and "max_drawdown_percent" in metrics_result.data:
                if metrics_result.data["max_drawdown_percent"] > max_drawdown * 100:
                    violations.append(f"Max drawdown exceeded: {metrics_result.data['max_drawdown_percent']}% > {max_drawdown*100}%")
            
            # Warning if too concentrated
            if len(self._positions) == 1 and self._balance < total_value * 0.3:
                warnings.append("Portfolio is concentrated in a single position")
            
            # Warning if no stop losses
            for symbol, pos in self._positions.items():
                if pos.stop_loss is None:
                    warnings.append(f"{symbol} has no stop loss set")
            
            return SkillResult.ok({
                "risk_compliant": len(violations) == 0,
                "violations": violations,
                "warnings": warnings,
                "checked_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Risk check failed: {str(e)}")
    
    # === Private Helper Methods ===
    
    def _calculate_diversification(self, allocations: list[dict]) -> float:
        """Calculate diversification score (0-100)."""
        if len(allocations) <= 1:
            return 0
        
        # Herfindahl-Hirschman Index (inverted)
        hhi = sum((a["percent"] / 100) ** 2 for a in allocations)
        # Convert to 0-100 score (lower HHI = more diversified)
        score = (1 - hhi) * 100
        return round(score, 2)


# Skill instance factory
def create_skill(config: SkillConfig) -> PortfolioSkill:
    """Create a portfolio skill instance."""
    return PortfolioSkill(config)
