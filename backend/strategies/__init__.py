"""
Trading strategies for Kazzy Agent
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger("Strategies")


class BaseStrategy(ABC):
    """Base class for all trading strategies"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def analyze(self, exchange, symbol: str, params: Dict = None) -> Dict[str, Any]:
        """
        Analyze market and generate trading signal
        Returns: {action: 'BUY'|'SELL'|'CLOSE'|'HOLD', confidence: float, ...}
        """
        pass

    async def get_market_data(self, exchange, symbol: str, timeframe: str = '1h',
                            limit: int = 100) -> list:
        """Get market data for analysis"""
        return await exchange.get_market_data(symbol, timeframe, limit)


class RSIStrategy(BaseStrategy):
    """RSI Mean Reversion Strategy"""

    def __init__(self):
        super().__init__("RSI Mean Reversion")

    async def analyze(self, exchange, symbol: str, params: Dict = None) -> Dict[str, Any]:
        """Generate signal based on RSI indicator"""
        params = params or {}

        # Strategy parameters
        rsi_period = params.get('rsi_period', 14)
        oversold = params.get('oversold', 30)
        overbought = params.get('overbought', 70)
        rsi_threshold_buy = params.get('rsi_threshold_buy', 35)  # Buy when RSI crosses above
        rsi_threshold_sell = params.get('rsi_threshold_sell', 65)  # Sell when RSI crosses below

        # Get market data
        data = await self.get_market_data(exchange, symbol, '1h', 50)
        if len(data) < rsi_period + 1:
            return {'action': 'HOLD', 'reason': 'Insufficient data'}

        # Calculate RSI
        rsi_value = self._calculate_rsi(data, rsi_period)

        # Get current price
        current_price = data[-1]['close'] if data else 0

        # Generate signal
        if rsi_value < rsi_threshold_buy:
            # Oversold - potential buy opportunity
            stop_loss = current_price * 0.98  # 2% stop loss
            take_profit = current_price * 1.04  # 4% take profit

            return {
                'action': 'BUY',
                'confidence': min((rsi_threshold_buy - rsi_value) / rsi_threshold_buy, 1.0),
                'reason': f'RSI oversold at {rsi_value:.1f}',
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'rsi': rsi_value,
                'price': current_price
            }

        elif rsi_value > rsi_threshold_sell:
            # Overbought - potential sell opportunity
            stop_loss = current_price * 1.02
            take_profit = current_price * 0.96

            return {
                'action': 'SELL',
                'confidence': min((rsi_value - rsi_threshold_sell) / (100 - rsi_threshold_sell), 1.0),
                'reason': f'RSI overbought at {rsi_value:.1f}',
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'rsi': rsi_value,
                'price': current_price
            }

        return {
            'action': 'HOLD',
            'confidence': 0,
            'reason': f'RSI neutral at {rsi_value:.1f}',
            'rsi': rsi_value,
            'price': current_price
        }

    def _calculate_rsi(self, data: list, period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(data) < period + 1:
            return 50

        closes = [c['close'] for c in data]

        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi


class MACrossoverStrategy(BaseStrategy):
    """Moving Average Crossover Strategy"""

    def __init__(self):
        super().__init__("MA Crossover")

    async def analyze(self, exchange, symbol: str, params: Dict = None) -> Dict[str, Any]:
        """Generate signal based on MA crossover"""
        params = params or {}

        fast_ma = params.get('fast_ma', 9)
        slow_ma = params.get('slow_ma', 21)

        # Get market data
        data = await self.get_market_data(exchange, symbol, '1h', max(slow_ma + 10, 50))
        if len(data) < slow_ma + 1:
            return {'action': 'HOLD', 'reason': 'Insufficient data'}

        # Calculate moving averages
        fast_ma_value = self._calculate_ma(data, fast_ma)
        slow_ma_value = self._calculate_ma(data, slow_ma)

        # Previous MA values for crossover detection
        prev_fast_ma = self._calculate_ma(data[:-1], fast_ma)
        prev_slow_ma = self._calculate_ma(data[:-1], slow_ma)

        current_price = data[-1]['close']

        # Golden Cross (Bullish)
        if prev_fast_ma <= prev_slow_ma and fast_ma_value > slow_ma_value:
            stop_loss = current_price * 0.97
            take_profit = current_price * 1.06

            return {
                'action': 'BUY',
                'confidence': 0.8,
                'reason': f'Golden Cross: Fast MA crossed above Slow MA',
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'fast_ma': fast_ma_value,
                'slow_ma': slow_ma_value,
                'price': current_price
            }

        # Death Cross (Bearish)
        elif prev_fast_ma >= prev_slow_ma and fast_ma_value < slow_ma_value:
            stop_loss = current_price * 1.03
            take_profit = current_price * 0.94

            return {
                'action': 'SELL',
                'confidence': 0.8,
                'reason': f'Death Cross: Fast MA crossed below Slow MA',
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'fast_ma': fast_ma_value,
                'slow_ma': slow_ma_value,
                'price': current_price
            }

        # Trend alignment
        elif fast_ma_value > slow_ma_value:
            return {
                'action': 'HOLD',
                'confidence': 0.3,
                'reason': f'Uptrend: Fast MA ({fast_ma_value:.4f}) > Slow MA ({slow_ma_value:.4f})',
                'fast_ma': fast_ma_value,
                'slow_ma': slow_ma_value,
                'price': current_price
            }

        else:
            return {
                'action': 'HOLD',
                'confidence': 0.3,
                'reason': f'Downtrend: Fast MA ({fast_ma_value:.4f}) < Slow MA ({slow_ma_value:.4f})',
                'fast_ma': fast_ma_value,
                'slow_ma': slow_ma_value,
                'price': current_price
            }

    def _calculate_ma(self, data: list, period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(data) < period:
            return 0

        closes = [c['close'] for c in data[-period:]]
        return sum(closes) / period


class GridStrategy(BaseStrategy):
    """Grid Trading Strategy"""

    def __init__(self):
        super().__init__("Grid Trading")

    async def analyze(self, exchange, symbol: str, params: Dict = None) -> Dict[str, Any]:
        """Generate signals based on grid levels"""
        params = params or {}

        grid_size = params.get('grid_size', 5)  # Number of grid levels
        grid_spacing = params.get('grid_spacing', 0.5)  # % between levels

        # Get current price
        data = await self.get_market_data(exchange, symbol, '1h', 1)
        if not data:
            return {'action': 'HOLD', 'reason': 'No market data'}

        current_price = data[-1]['close']
        volatility = self._calculate_volatility(data)

        # Calculate grid levels
        levels = []
        for i in range(-grid_size, grid_size + 1):
            level = current_price * (1 + (i * grid_spacing / 100))
            levels.append(level)

        # Find nearest grid level
        nearest_level = min(levels, key=lambda x: abs(x - current_price))
        distance_pct = abs(current_price - nearest_level) / current_price * 100

        # If price is near a grid line
        if distance_pct < 0.1:
            # At grid line - check direction
            if current_price < nearest_level:
                return {
                    'action': 'BUY',
                    'confidence': 0.7,
                    'reason': f'Price near grid support at {nearest_level:.4f}',
                    'grid_level': nearest_level,
                    'price': current_price
                }
            else:
                return {
                    'action': 'SELL',
                    'confidence': 0.7,
                    'reason': f'Price near grid resistance at {nearest_level:.4f}',
                    'grid_level': nearest_level,
                    'price': current_price
                }

        return {
            'action': 'HOLD',
            'confidence': 0,
            'reason': f'No grid line nearby. Nearest: {nearest_level:.4f}',
            'grid_level': nearest_level,
            'price': current_price
        }

    def _calculate_volatility(self, data: list, period: int = 20) -> float:
        """Calculate price volatility"""
        if len(data) < 2:
            return 0

        closes = [c['close'] for c in data[-period:]]
        if len(closes) < 2:
            return 0

        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        volatility = (sum([r*r for r in returns]) / len(returns)) ** 0.5

        return volatility * 100  # As percentage
