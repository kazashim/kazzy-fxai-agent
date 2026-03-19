"""
Kazzy Agent Data Aggregation & Learning System
Fetches all data from connected exchanges and uses it to learn and improve
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import asyncio

logger = logging.getLogger("KazzyLearning")

# Data structures for comprehensive trading data
@dataclass
class AccountData:
    """Complete account data from exchange"""
    exchange: str
    total_balance: float
    available_balance: float
    equity: float
    margin_used: float
    unrealized_pnl: float
    assets: Dict[str, Dict[str, float]] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class TradeRecord:
    """Individual trade record for learning"""
    id: str
    exchange: str
    symbol: str
    side: str  # buy/sell
    quantity: float
    entry_price: float
    exit_price: float
    pnl: float
    pnl_percent: float
    fees: float
    entry_time: str
    exit_time: str
    duration_minutes: float
    strategy_used: str = ""
    market_condition: str = ""  # trending, volatile, quiet
    signal_source: str = ""  # ai, manual, signal
    tags: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class PositionData:
    """Current position data"""
    id: str
    exchange: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    leverage: int
    stop_loss: float = 0
    take_profit: float = 0
    open_time: str = ""
    margin_used: float = 0


@dataclass
class OrderData:
    """Order history"""
    id: str
    exchange: str
    symbol: str
    side: str
    order_type: str  # market, limit, stop
    status: str  # filled, cancelled, pending
    quantity: float
    price: float
    filled_price: float
    created_time: str
    filled_time: str = ""


@dataclass
class MarketSnapshot:
    """Market data snapshot"""
    symbol: str
    current_price: float
    bid: float
    ask: float
    spread: float
    volume_24h: float
    high_24h: float
    low_24h: float
    change_24h: float
    change_percent_24h: float
    timestamp: str = ""


class DataAggregator:
    """
    Comprehensive data aggregation from all connected exchanges
    Fetches: balances, positions, orders, trade history, market data
    """

    def __init__(self):
        self.exchange_connectors = {}
        self.cache = {}
        self.cache_ttl = 30  # seconds

    async def aggregate_all_data(self, exchanges: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate all data from connected exchanges"""
        logger.info("📊 Aggregating data from all exchanges...")

        aggregated = {
            "accounts": [],
            "positions": [],
            "orders": [],
            "trades": [],
            "markets": {},
            "total_value_usd": 0,
            "timestamp": datetime.now().isoformat()
        }

        for exchange_name, connector in exchanges.items():
            if not connector or not getattr(connector, 'is_connected', False):
                continue

            try:
                # Fetch account data
                account = await self._fetch_account_data(exchange_name, connector)
                if account:
                    aggregated["accounts"].append(account)
                    aggregated["total_value_usd"] += account.total_balance

                # Fetch positions
                positions = await self._fetch_positions(exchange_name, connector)
                aggregated["positions"].extend(positions)

                # Fetch orders
                orders = await self._fetch_orders(exchange_name, connector)
                aggregated["orders"].extend(orders)

                # Fetch trade history
                trades = await self._fetch_trade_history(exchange_name, connector)
                aggregated["trades"].extend(trades)

                # Fetch market data for common symbols
                markets = await self._fetch_market_data(exchange_name, connector)
                aggregated["markets"].update(markets)

            except Exception as e:
                logger.error(f"Error aggregating {exchange_name}: {e}")

        logger.info(f"✅ Aggregated: {len(aggregated['accounts'])} accounts, "
                   f"{len(aggregated['positions'])} positions, "
                   f"{len(aggregated['trades'])} trades")

        return aggregated

    async def _fetch_account_data(self, exchange: str, connector: Any) -> Optional[AccountData]:
        """Fetch complete account data"""
        try:
            balance = await connector.get_balance()
            if not balance:
                return None

            return AccountData(
                exchange=exchange,
                total_balance=balance.get('total', 0),
                available_balance=balance.get('free', 0),
                equity=balance.get('total', 0),
                margin_used=balance.get('used', 0),
                unrealized_pnl=balance.get('total', 0) - balance.get('free', 0),
                assets=balance.get('info', {})
            )
        except Exception as e:
            logger.error(f"Error fetching account data from {exchange}: {e}")
            return None

    async def _fetch_positions(self, exchange: str, connector: Any) -> List[PositionData]:
        """Fetch all open positions"""
        positions = []
        try:
            raw_positions = await connector.get_positions()
            for i, pos in enumerate(raw_positions):
                positions.append(PositionData(
                    id=f"{exchange}_{i}_{pos.get('symbol', 'unknown')}",
                    exchange=exchange,
                    symbol=pos.get('symbol', 'UNKNOWN'),
                    side=pos.get('side', 'buy'),
                    quantity=float(pos.get('amount', 0)),
                    entry_price=float(pos.get('entryPrice', 0)),
                    current_price=float(pos.get('price', 0)),
                    unrealized_pnl=float(pos.get('pnl', 0)),
                    leverage=int(pos.get('leverage', 1)),
                    stop_loss=float(pos.get('stopLoss', 0)),
                    take_profit=float(pos.get('takeProfit', 0)),
                    margin_used=float(pos.get('margin', 0))
                ))
        except Exception as e:
            logger.error(f"Error fetching positions from {exchange}: {e}")
        return positions

    async def _fetch_orders(self, exchange: str, connector: Any) -> List[OrderData]:
        """Fetch order history"""
        orders = []
        try:
            # Get open orders
            open_orders = await connector.fetch_open_orders()
            for i, order in enumerate(open_orders[:50]):  # Last 50
                orders.append(OrderData(
                    id=str(order.get('id', i)),
                    exchange=exchange,
                    symbol=order.get('symbol', 'UNKNOWN'),
                    side=order.get('side', 'buy'),
                    order_type=order.get('type', 'market'),
                    status='open',
                    quantity=float(order.get('amount', 0)),
                    price=float(order.get('price', 0)),
                    filled_price=float(order.get('filled', 0)),
                    created_time=str(order.get('timestamp', ''))
                ))
        except Exception as e:
            logger.error(f"Error fetching orders from {exchange}: {e}")
        return orders

    async def _fetch_trade_history(self, exchange: str, connector: Any) -> List[TradeRecord]:
        """Fetch trade history for learning"""
        trades = []
        try:
            # Fetch recent closed trades
            my_trades = await connector.fetch_my_trades(limit=100)

            for i, trade in enumerate(my_trades):
                entry_price = float(trade.get('price', 0))
                fees = float(trade.get('fee', 0))

                # Calculate PnL (simplified)
                pnl = 0
                pnl_percent = 0

                trades.append(TradeRecord(
                    id=f"{exchange}_{trade.get('id', i)}",
                    exchange=exchange,
                    symbol=trade.get('symbol', 'UNKNOWN'),
                    side=trade.get('side', 'buy'),
                    quantity=float(trade.get('amount', 0)),
                    entry_price=entry_price,
                    exit_price=entry_price,  # For closed trades, we'd need both entry/exit
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                    fees=fees,
                    entry_time=str(trade.get('timestamp', '')),
                    exit_time=str(trade.get('timestamp', '')),
                    duration_minutes=0
                ))
        except Exception as e:
            logger.error(f"Error fetching trades from {exchange}: {e}")
        return trades

    async def _fetch_market_data(self, exchange: str, connector: Any) -> Dict[str, MarketSnapshot]:
        """Fetch current market data"""
        markets = {}
        symbols = ['BTC/USDT', 'ETH/USDT', 'EUR/USD', 'XAU/USD', 'AAPL', 'TSLA']

        try:
            for symbol in symbols:
                try:
                    ticker = await connector.fetch_ticker(symbol)
                    markets[symbol] = MarketSnapshot(
                        symbol=symbol,
                        current_price=float(ticker.get('last', 0)),
                        bid=float(ticker.get('bid', 0)),
                        ask=float(ticker.get('ask', 0)),
                        spread=float(ticker.get('ask', 0)) - float(ticker.get('bid', 0)),
                        volume_24h=float(ticker.get('volume', 0)),
                        high_24h=float(ticker.get('high', 0)),
                        low_24h=float(ticker.get('low', 0)),
                        change_24h=float(ticker.get('change', 0)),
                        change_percent_24h=float(ticker.get('percentage', 0))
                    )
                except:
                    pass
        except Exception as e:
            logger.error(f"Error fetching market data from {exchange}: {e}")
        return markets


class AILearningSystem:
    """
    AI Learning System that analyzes trading data and improves performance
    """

    def __init__(self):
        self.trade_history: List[TradeRecord] = []
        self.performance_metrics = {}
        self.strategy_performance = defaultdict(lambda: {"wins": 0, "losses": 0, "total_pnl": 0})
        self.market_condition_performance = defaultdict(lambda: {"wins": 0, "losses": 0})
        self.patterns_detected = []
        self.improvements_suggested = []

    async def learn_from_data(self, aggregated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main learning function - analyze all data and generate insights"""
        logger.info("🧠 AI Learning from trading data...")

        # Update trade history
        self.trade_history = [TradeRecord(**t) if isinstance(t, dict) else t
                              for t in aggregated_data.get("trades", [])]

        # Calculate performance metrics
        self.performance_metrics = self._calculate_performance_metrics()

        # Analyze strategy performance
        strategy_analysis = self._analyze_strategy_performance()

        # Analyze market conditions
        market_analysis = self._analyze_market_conditions()

        # Detect patterns
        patterns = self._detect_patterns()

        # Generate improvements
        improvements = self._generate_improvements()

        insights = {
            "performance_metrics": self.performance_metrics,
            "strategy_analysis": strategy_analysis,
            "market_analysis": market_analysis,
            "detected_patterns": patterns,
            "suggested_improvements": improvements,
            "total_trades_analyzed": len(self.trade_history),
            "learning_version": "2.0",
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"✅ Learning complete: {len(improvements)} improvements suggested")
        return insights

    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        if not self.trade_history:
            return {"status": "No trades to analyze"}

        wins = [t for t in self.trade_history if t.pnl > 0]
        losses = [t for t in self.trade_history if t.pnl <= 0]

        win_rate = len(wins) / len(self.trade_history) * 100 if self.trade_history else 0

        total_pnl = sum(t.pnl for t in self.trade_history)
        total_fees = sum(t.fees for t in self.trade_history)

        avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.pnl for t in losses) / len(losses) if losses else 0

        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0

        # Calculate drawdown (simplified)
        running_pnl = 0
        max_pnl = 0
        max_drawdown = 0
        for trade in self.trade_history:
            running_pnl += trade.pnl
            max_pnl = max(max_pnl, running_pnl)
            drawdown = max_pnl - running_pnl
            max_drawdown = max(max_drawdown, drawdown)

        return {
            "total_trades": len(self.trade_history),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "total_fees": round(total_fees, 2),
            "net_pnl": round(total_pnl - total_fees, 2),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown": round(max_drawdown, 2),
            "best_trade": max((t.pnl for t in self.trade_history), default=0),
            "worst_trade": min((t.pnl for t in self.trade_history), default=0),
        }

    def _analyze_strategy_performance(self) -> Dict[str, Any]:
        """Analyze performance by strategy"""
        for trade in self.trade_history:
            strategy = trade.strategy_used or "unknown"
            self.strategy_performance[strategy]["total_trades"] += 1
            if trade.pnl > 0:
                self.strategy_performance[strategy]["wins"] += 1
                self.strategy_performance[strategy]["total_pnl"] += trade.pnl
            else:
                self.strategy_performance[strategy]["losses"] += 1
                self.strategy_performance[strategy]["total_pnl"] += trade.pnl

        # Find best and worst strategies
        strategy_stats = []
        for strategy, stats in self.strategy_performance.items():
            total = stats["wins"] + stats["losses"]
            win_rate = (stats["wins"] / total * 100) if total > 0 else 0
            strategy_stats.append({
                "strategy": strategy,
                "total_trades": total,
                "win_rate": round(win_rate, 2),
                "total_pnl": round(stats["total_pnl"], 2)
            })

        strategy_stats.sort(key=lambda x: x["total_pnl"], reverse=True)

        return {
            "strategies": strategy_stats,
            "best_strategy": strategy_stats[0] if strategy_stats else None,
            "worst_strategy": strategy_stats[-1] if strategy_stats else None
        }

    def _analyze_market_conditions(self) -> Dict[str, Any]:
        """Analyze performance by market condition"""
        for trade in self.trade_history:
            condition = trade.market_condition or "unknown"
            if trade.pnl > 0:
                self.market_condition_performance[condition]["wins"] += 1
            else:
                self.market_condition_performance[condition]["losses"] += 1

        conditions = []
        for condition, stats in self.market_condition_performance.items():
            total = stats["wins"] + stats["losses"]
            win_rate = (stats["wins"] / total * 100) if total > 0 else 0
            conditions.append({
                "condition": condition,
                "trades": total,
                "win_rate": round(win_rate, 2)
            })

        return {"market_conditions": conditions}

    def _detect_patterns(self) -> List[Dict[str, Any]]:
        """Detect trading patterns from history"""
        patterns = []

        # Pattern 1: Time-based
        if len(self.trade_history) >= 10:
            # Check for time-of-day patterns
            morning_trades = [t for t in self.trade_history if 6 <= int(t.entry_time[11:13] if t.entry_time else 12) <= 12]
            afternoon_trades = [t for t in self.trade_history if 12 <= int(t.entry_time[11:13] if t.entry_time else 12) <= 18]

            if morning_trades and afternoon_trades:
                morning_win_rate = len([t for t in morning_trades if t.pnl > 0]) / len(morning_trades) * 100
                afternoon_win_rate = len([t for t in afternoon_trades if t.pnl > 0]) / len(afternoon_trades) * 100

                if morning_win_rate > afternoon_win_rate + 15:
                    patterns.append({
                        "type": "time_of_day",
                        "description": f"Trading in morning shows {round(morning_win_rate, 1)}% win rate vs {round(afternoon_win_rate, 1)}% in afternoon",
                        "recommendation": "Focus trading during morning hours"
                    })

        # Pattern 2: Position size correlation
        winning_trades = [t for t in self.trade_history if t.pnl > 0]
        losing_trades = [t for t in self.trade_history if t.pnl <= 0]

        if winning_trades and losing_trades:
            avg_win_size = sum(t.quantity for t in winning_trades) / len(winning_trades)
            avg_loss_size = sum(t.quantity for t in losing_trades) / len(losing_trades)

            if avg_win_size > avg_loss_size * 1.3:
                patterns.append({
                    "type": "position_size",
                    "description": "Winning trades tend to have larger position sizes",
                    "recommendation": "Consider increasing position size on high-confidence trades"
                })
            elif avg_loss_size > avg_win_size * 1.3:
                patterns.append({
                    "type": "position_size",
                    "description": "Losing trades have larger position sizes - potential risk issue",
                    "recommendation": "Reduce position size on lower confidence trades"
                })

        # Pattern 3: Stop loss effectiveness
        trades_with_sl = [t for t in self.trade_history if t.stop_loss > 0]
        if trades_with_sl:
            sl_hit = len([t for t in trades_with_sl if t.pnl < 0])
            sl_win_rate = (1 - sl_hit / len(trades_with_sl)) * 100

            if sl_win_rate < 40:
                patterns.append({
                    "type": "stop_loss",
                    "description": f"Stop loss hit {sl_hit}/{len(trades_with_sl)} times - {round(sl_win_rate, 1)}% success rate",
                    "recommendation": "Consider widening stop loss or improving entry timing"
                })

        return patterns

    def _generate_improvements(self) -> List[Dict[str, Any]]:
        """Generate AI-powered improvement suggestions"""
        improvements = []

        if not self.performance_metrics or self.performance_metrics.get("status"):
            return [{"type": "data", "message": "Need more trade data to generate improvements"}]

        # Improvement 1: Win rate optimization
        win_rate = self.performance_metrics.get("win_rate", 0)
        if win_rate < 45:
            improvements.append({
                "priority": "high",
                "category": "win_rate",
                "issue": f"Win rate is {win_rate}% - below target",
                "suggestion": "Focus on higher probability setups. Wait for stronger signals before entering trades.",
                "expected_impact": "5-10% improvement in win rate"
            })

        # Improvement 2: Risk/Reward optimization
        profit_factor = self.performance_metrics.get("profit_factor", 0)
        if profit_factor < 1.5:
            improvements.append({
                "priority": "medium",
                "category": "risk_reward",
                "issue": f"Profit factor is {profit_factor} - should be >2",
                "suggestion": "Adjust take profit to be at least 2x the stop loss size",
                "expected_impact": "Improved risk/reward ratio"
            })

        # Improvement 3: Overtrading
        if len(self.trade_history) > 50:
            daily_trades = len(self.trade_history) / max(1, (datetime.now() - datetime.fromisoformat(self.trade_history[0].entry_time)).days or 1)
            if daily_trades > 5:
                improvements.append({
                    "priority": "medium",
                    "category": "overtrading",
                    "issue": f"Average {round(daily_trades, 1)} trades per day - potential overtrading",
                    "suggestion": "Reduce trading frequency. Focus on quality over quantity.",
                    "expected_impact": "Better trade quality and reduced fees"
                })

        # Improvement 4: Best performing time
        if self._analyze_strategy_performance().get("best_strategy"):
            best = self._analyze_strategy_performance()["best_strategy"]
            improvements.append({
                "priority": "low",
                "category": "optimization",
                "issue": f"Best strategy: {best['strategy']} with {best['win_rate']}% win rate",
                "suggestion": f"Increase allocation to {best['strategy']} strategy",
                "expected_impact": "Better overall performance"
            })

        # Improvement 5: Position sizing
        if self.performance_metrics.get("max_drawdown", 0) > 20:
            improvements.append({
                "priority": "high",
                "category": "risk_management",
                "issue": f"Max drawdown is {self.performance_metrics.get('max_drawdown')}%",
                "suggestion": "Reduce position sizes by 25% to lower drawdown risk",
                "expected_impact": "Reduced risk and drawdown"
            })

        self.improvements_suggested = improvements
        return improvements

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of all learning insights"""
        return {
            "performance": self.performance_metrics,
            "total_trades": len(self.trade_history),
            "patterns_found": len(self.patterns_detected),
            "improvements_available": len(self.improvements_suggested),
            "latest_improvements": self.improvements_suggested[:3]
        }


# Global instances
data_aggregator = DataAggregator()
ai_learning_system = AILearningSystem()
