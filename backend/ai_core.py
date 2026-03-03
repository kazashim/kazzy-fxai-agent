"""
Kazzy Agent AI Core Module
Advanced AI-powered market analysis and autonomous trading
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import random

logger = logging.getLogger("KazzyAI")


class AIState(Enum):
    """AI Agent states"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    EXECUTING = "executing"
    LEARNING = "learning"
    EMERGENCY = "emergency"


class AISentiment(Enum):
    """Market sentiment scores"""
    VERY_BEARISH = -2
    BEARISH = -1
    NEUTRAL = 0
    BULLISH = 1
    VERY_BULLISH = 2


class MarketAnalyzer:
    """AI-powered market analysis engine"""

    def __init__(self):
        self.name = "Kazzy AI Core"
        self.version = "2.0.0"

    async def analyze_market(self, symbol: str, market_data: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive market analysis using multiple indicators and AI
        """
        logger.info(f"🔍 AI Analyzing {symbol}...")

        # Extract price data
        closes = [c['close'] for c in market_data] if market_data else []
        highs = [c['high'] for c in market_data] if market_data else []
        lows = [c['low'] for c in market_data] if market_data else []
        volumes = [c['volume'] for c in market_data] if market_data else []

        if not closes:
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': 'Insufficient market data'
            }

        # Technical Analysis
        rsi = self._calculate_rsi(closes)
        macd = self._calculate_macd(closes)
        trend = self._determine_trend(closes)
        volatility = self._calculate_volatility(closes)

        # Support/Resistance
        support, resistance = self._find_support_resistance(highs, lows, closes)

        # AI Confidence Calculation
        confidence_factors = []

        # RSI Factor
        if rsi < 30:
            confidence_factors.append(('RSI_OVERSOLD', 0.8, 'RSI at {rsi:.1f} - oversold condition'))
        elif rsi > 70:
            confidence_factors.append(('RSI_OVERBOUGHT', -0.7, 'RSI at {rsi:.1f} - overbought condition'))
        else:
            confidence_factors.append(('RSI_NEUTRAL', 0.3, 'RSI neutral at {rsi:.1f}'))

        # Trend Factor
        if trend == 'BULLISH':
            confidence_factors.append(('TREND', 0.7, f'Uptrend detected'))
        elif trend == 'BEARISH':
            confidence_factors.append(('TREND', -0.7, f'Downtrend detected'))
        else:
            confidence_factors.append(('TREND', 0.2, 'Sideways trend'))

        # MACD Factor
        if macd > 0:
            confidence_factors.append(('MACD', 0.5, 'MACD bullish crossover'))
        else:
            confidence_factors.append(('MACD', -0.5, 'MACD bearish crossover'))

        # Calculate overall confidence
        total_confidence = sum(f[1] * 0.3 for f in confidence_factors)  # Base 30%
        base_confidence = 50 + (total_confidence * 50)  # Scale to 0-100

        # Generate signal
        if base_confidence > 65 and rsi < 60:
            signal = 'BUY'
            reason = f"AI Signal: Bullish confluence. RSI={rsi:.1f}, Trend={trend}, Confidence={base_confidence:.0f}%"
        elif base_confidence < 35 and rsi > 40:
            signal = 'SELL'
            reason = f"AI Signal: Bearish confluence. RSI={rsi:.1f}, Trend={trend}, Confidence={abs(base_confidence):.0f}%"
        else:
            signal = 'HOLD'
            reason = f"AI Signal: No clear setup. Confidence={base_confidence:.0f}%"

        return {
            'signal': signal,
            'confidence': base_confidence,
            'reason': reason,
            'indicators': {
                'rsi': rsi,
                'macd': macd,
                'trend': trend,
                'volatility': volatility,
                'support': support,
                'resistance': resistance
            },
            'factors': confidence_factors,
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(closes) < period + 1:
            return 50

        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, closes: List[float]) -> float:
        """Calculate MACD indicator"""
        if len(closes) < 26:
            return 0

        # EMA 12
        ema12 = self._ema(closes, 12)
        # EMA 26
        ema26 = self._ema(closes, 26)

        return ema12 - ema26

    def _ema(self, data: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return data[-1] if data else 0

        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period

        for price in data[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def _determine_trend(self, closes: List[float]) -> str:
        """Determine market trend"""
        if len(closes) < 50:
            return 'SIDEWAYS'

        sma20 = sum(closes[-20:]) / 20
        sma50 = sum(closes[-50:]) / 50

        if sma20 > sma50 * 1.02:
            return 'BULLISH'
        elif sma20 < sma50 * 0.98:
            return 'BEARISH'
        return 'SIDEWAYS'

    def _calculate_volatility(self, closes: List[float]) -> float:
        """Calculate market volatility (ATR-based)"""
        if len(closes) < 14:
            return 0

        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        return (sum(r*r for r in returns[-14:]) / 14) ** 0.5 * 100

    def _find_support_resistance(self, highs: List[float], lows: List[float],
                                  closes: List[float]) -> tuple:
        """Find support and resistance levels"""
        if not highs or not lows:
            return 0, 0

        current = closes[-1] if closes else 0

        # Simple pivot-based S/R
        resistance = max(highs[-20:]) if len(highs) >= 20 else max(highs)
        support = min(lows[-20:]) if len(lows) >= 20 else min(lows)

        return support, resistance


class AIDecisionEngine:
    """AI Decision making and trade execution logic"""

    def __init__(self, risk_manager):
        self.risk_manager = risk_manager
        self.market_analyzer = MarketAnalyzer()
        self.state = AIState.IDLE
        self.thought_log = []

    async def evaluate_trade(self, symbol: str, market_data: List[Dict],
                           balance: float) -> Dict[str, Any]:
        """
        AI evaluates whether to execute a trade
        """
        self.state = AIState.ANALYZING
        self._log_thought(f"Starting analysis for {symbol}")

        # Analyze market
        analysis = await self.market_analyzer.analyze_market(symbol, market_data)

        self._log_thought(f"Analysis complete: {analysis['signal']} ({analysis['confidence']:.0f}% confidence)")

        # Check risk rules
        risk_check = self.risk_manager.validate_trade(
            balance=balance,
            risk_percent=self.risk_manager.max_risk_per_trade,
            symbol=symbol,
            entry_price=market_data[-1]['close'] if market_data else 0,
            stop_loss=None
        )

        if not risk_check['approved']:
            self._log_thought(f"Trade rejected: {risk_check['reason']}")
            return {
                'action': 'REJECTED',
                'reason': risk_check['reason'],
                'ai_analysis': analysis
            }

        # High confidence signal
        if analysis['confidence'] > 70:
            self.state = AIState.EXECUTING
            self._log_thought(f"High confidence signal - preparing execution")

            position_size = risk_check['position_size']

            return {
                'action': analysis['signal'],
                'confidence': analysis['confidence'],
                'position_size': position_size,
                'reason': analysis['reason'],
                'indicators': analysis['indicators']
            }

        # Medium confidence - hold
        elif analysis['confidence'] > 50:
            self._log_thought(f"Medium confidence - waiting for better setup")
            return {
                'action': 'HOLD',
                'confidence': analysis['confidence'],
                'reason': 'Confidence below threshold'
            }

        # Low confidence
        else:
            self._log_thought(f"Low confidence - no action")
            return {
                'action': 'HOLD',
                'confidence': analysis['confidence'],
                'reason': 'Market conditions unclear'
            }

    def _log_thought(self, thought: str):
        """Log AI thought process"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {thought}"
        self.thought_log.append(log_entry)
        logger.info(f"🤖 {log_entry}")

    def get_thoughts(self) -> List[str]:
        """Get AI thought history"""
        return self.thought_log[-20:]  # Last 20 thoughts


class SignalGenerator:
    """AI-powered signal generation"""

    def __init__(self):
        self.active_signals = []

    async def generate_signals(self, symbols: List[str],
                              market_data: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate AI signals for multiple symbols"""
        signals = []
        analyzer = MarketAnalyzer()

        for symbol in symbols:
            data = market_data.get(symbol, [])
            if not data:
                continue

            analysis = await analyzer.analyze_market(symbol, data)

            if analysis['signal'] in ['BUY', 'SELL']:
                signal = {
                    'id': f"AI_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'symbol': symbol,
                    'direction': analysis['signal'].lower(),
                    'confidence': analysis['confidence'],
                    'reason': analysis['reason'],
                    'entry_zone': self._calculate_entry(analysis, data),
                    'stop_loss': self._calculate_sl(analysis, data),
                    'take_profit': self._calculate_tp(analysis, data),
                    'timestamp': datetime.now().isoformat(),
                    'ai_generated': True
                }
                signals.append(signal)

        self.active_signals = signals
        return signals

    def _calculate_entry(self, analysis: Dict, data: List[Dict]) -> str:
        """Calculate entry zone"""
        current = data[-1]['close'] if data else 0

        if analysis['signal'] == 'BUY':
            return f"{current * 0.995:.4f}-{current:.4f}"
        else:
            return f"{current:.4f}-{current * 1.005:.4f}"

    def _calculate_sl(self, analysis: Dict, data: List[Dict]) -> str:
        """Calculate stop loss"""
        current = data[-1]['close'] if data else 0
        volatility = analysis.get('indicators', {}).get('volatility', 1)

        # Dynamic SL based on volatility
        sl_distance = current * (volatility / 100) * 2

        if analysis['signal'] == 'BUY':
            return f"{current - sl_distance:.4f}"
        else:
            return f"{current + sl_distance:.4f}"

    def _calculate_tp(self, analysis: Dict, data: List[Dict]) -> str:
        """Calculate take profit"""
        current = data[-1]['close'] if data else 0

        # Risk:Reward 1:2
        volatility = analysis.get('indicators', {}).get('volatility', 1)
        sl_distance = current * (volatility / 100) * 2

        if analysis['signal'] == 'BUY':
            return f"{current + (sl_distance * 2):.4f}"
        else:
            return f"{current - (sl_distance * 2):.4f}"


class NLPProcessor:
    """Natural Language Processing for trading commands"""

    def __init__(self, decision_engine: AIDecisionEngine):
        self.engine = decision_engine

    async def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process natural language trading commands
        """
        command = command.lower().strip()
        logger.info(f"🎯 Processing command: {command}")

        # Buy commands
        if any(word in command for word in ['buy', 'long', 'purchase', 'enter']):
            symbol = self._extract_symbol(command)
            return {
                'action': 'BUY',
                'symbol': symbol,
                'confidence': 85,
                'reason': f"User requested buy for {symbol}"
            }

        # Sell commands
        elif any(word in command for word in ['sell', 'short', 'close']):
            symbol = self._extract_symbol(command)
            return {
                'action': 'SELL',
                'symbol': symbol,
                'confidence': 85,
                'reason': f"User requested sell for {symbol}"
            }

        # Analysis commands
        elif any(word in command for word in ['analyze', 'analysis', 'what about']):
            symbol = self._extract_symbol(command)
            return {
                'action': 'ANALYZE',
                'symbol': symbol,
                'reason': f"User requested analysis for {symbol}"
            }

        # Status commands
        elif any(word in command for word in ['status', 'position', 'portfolio']):
            return {
                'action': 'STATUS',
                'reason': 'Reporting portfolio status'
            }

        # Stop commands
        elif any(word in command for word in ['stop', 'emergency', 'halt']):
            return {
                'action': 'EMERGENCY_STOP',
                'reason': 'Emergency stop requested'
            }

        # Unknown command
        return {
            'action': 'UNKNOWN',
            'reason': 'Command not recognized'
        }

    def _extract_symbol(self, command: str) -> str:
        """Extract trading symbol from command"""
        # Common symbols
        symbols = {
            'btc': 'BTC/USDT',
            'bitcoin': 'BTC/USDT',
            'eth': 'ETH/USDT',
            'ethereum': 'ETH/USDT',
            'eur': 'EUR/USD',
            'euro': 'EUR/USD',
            'gbp': 'GBP/USD',
            'gold': 'XAU/USD',
            'xau': 'XAU/USD',
            'jpy': 'USD/JPY'
        }

        for key, symbol in symbols.items():
            if key in command:
                return symbol

        return 'BTC/USDT'  # Default


class AILearningSystem:
    """Machine learning and adaptation system"""

    def __init__(self):
        self.trade_history = []
        self.strategy_performance = {}
        self.learned_patterns = []

    def record_trade(self, trade: Dict[str, Any]):
        """Record trade for learning"""
        self.trade_history.append({
            **trade,
            'timestamp': datetime.now().isoformat()
        })

        # Update strategy performance
        strategy = trade.get('strategy', 'unknown')
        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = {'wins': 0, 'losses': 0, 'total': 0}

        if trade.get('pnl', 0) > 0:
            self.strategy_performance[strategy]['wins'] += 1
        else:
            self.strategy_performance[strategy]['losses'] += 1

        self.strategy_performance[strategy]['total'] += 1

        logger.info(f"📚 Recorded trade: {strategy} - PnL: ${trade.get('pnl', 0):.2f}")

    def get_recommendations(self) -> Dict[str, Any]:
        """Get AI recommendations based on learned data"""

        if not self.strategy_performance:
            return {
                'recommendations': [],
                'overall_performance': 'No data yet'
            }

        recommendations = []

        # Analyze each strategy
        for strategy, stats in self.strategy_performance.items():
            win_rate = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0

            if win_rate > 60 and stats['total'] > 10:
                recommendations.append({
                    'strategy': strategy,
                    'action': 'INCREASE',
                    'win_rate': win_rate,
                    'reason': f'Win rate {win_rate:.1f}% exceeds threshold'
                })
            elif win_rate < 40 and stats['total'] > 10:
                recommendations.append({
                    'strategy': strategy,
                    'action': 'DECREASE',
                    'win_rate': win_rate,
                    'reason': f'Win rate {win_rate:.1f}% below threshold'
                })

        return {
            'recommendations': recommendations,
            'total_trades': sum(s['total'] for s in self.strategy_performance.values()),
            'strategy_performance': self.strategy_performance
        }

    def should_continue_trading(self) -> bool:
        """AI decides if trading should continue"""
        total_wins = sum(s['wins'] for s in self.strategy_performance.values())
        total_losses = sum(s['losses'] for s in self.strategy_performance.values())
        total = total_wins + total_losses

        if total < 20:
            return True  # Not enough data

        win_rate = total_wins / total

        # Stop if losing streak
        if total_losses > total_wins * 2:
            logger.warning("📉 AI recommends pause - losing streak detected")
            return False

        return True
