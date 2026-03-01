"""
Risk Management Module for Kazzy Agent
Implements position sizing, risk limits, and trade validation
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("RiskManager")


class RiskManager:
    """Risk management and position sizing engine"""

    def __init__(self, max_risk_per_trade: float = 2.0, max_daily_loss: float = 5.0,
                 max_positions: int = 5, max_correlation: float = 0.7):
        self.max_risk_per_trade = max_risk_per_trade  # % of account
        self.max_daily_loss = max_daily_loss  # % of account
        self.max_positions = max_positions
        self.max_correlation = max_correlation  # Max correlation between positions

        self.daily_loss = 0.0
        self.daily_trades = 0
        self.open_positions = 0
        self.last_reset = None

    def validate_trade(self, balance: float, risk_percent: float, symbol: str,
                     entry_price: float, stop_loss: Optional[float] = None,
                     take_profit: Optional[float] = None) -> Dict[str, Any]:
        """
        Validate a trade against risk rules
        Returns: {approved: bool, reason: str, position_size: float}
        """
        # Check if balance is valid
        if balance <= 0:
            return {
                'approved': False,
                'reason': 'Invalid account balance',
                'position_size': 0
            }

        # Check max positions
        if self.open_positions >= self.max_positions:
            return {
                'approved': False,
                'reason': f'Maximum positions ({self.max_positions}) reached',
                'position_size': 0
            }

        # Check risk per trade
        if risk_percent > self.max_risk_per_trade:
            return {
                'approved': False,
                'reason': f'Risk {risk_percent}% exceeds max {self.max_risk_per_trade}%',
                'position_size': 0
            }

        # Check daily loss limit
        if self.daily_loss <= -self.max_daily_loss:
            return {
                'approved': False,
                'reason': f'Daily loss limit ({self.max_daily_loss}%) reached',
                'position_size': 0
            }

        # Calculate position size based on risk
        position_size = self.calculate_position_size(
            balance=balance,
            risk_percent=risk_percent,
            entry_price=entry_price,
            stop_loss=stop_loss
        )

        if position_size <= 0:
            return {
                'approved': False,
                'reason': 'Calculated position size is too small',
                'position_size': 0
            }

        return {
            'approved': True,
            'reason': 'Trade approved',
            'position_size': position_size,
            'risk_amount': balance * (risk_percent / 100)
        }

    def calculate_position_size(self, balance: float, risk_percent: float,
                              entry_price: float, stop_loss: Optional[float] = None) -> float:
        """
        Calculate position size based on risk management rules
        Uses fixed fractional position sizing
        """
        if entry_price <= 0:
            return 0

        risk_amount = balance * (risk_percent / 100)

        # If no stop loss, use a default 2% move
        if stop_loss is None:
            stop_loss_pct = 0.02
        else:
            stop_loss_pct = abs(entry_price - stop_loss) / entry_price

        if stop_loss_pct <= 0:
            return 0

        # Calculate position size
        position_size = risk_amount / (entry_price * stop_loss_pct)

        # Round to appropriate decimals
        # Forex pairs: 0.01 lots (micro lots)
        # Crypto: 0.0001 BTC, etc.
        if 'USD' in str(entry_price) and entry_price < 1000:
            # Likely forex
            position_size = round(position_size, 2)
        else:
            # Likely crypto
            position_size = round(position_size, 6)

        return max(position_size, 0.01)  # Minimum 0.01

    def calculate_risk_reward(self, entry_price: float, stop_loss: float,
                            take_profit: float) -> float:
        """Calculate risk-reward ratio"""
        if stop_loss <= 0 or take_profit <= 0:
            return 0

        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)

        if risk <= 0:
            return 0

        return reward / risk

    def check_correlation(self, positions: list, new_symbol: str) -> Dict[str, Any]:
        """
        Check correlation with existing positions
        Returns correlation warning if too high
        """
        if not positions:
            return {'safe': True}

        # Simplified correlation check
        # In production, would use actual correlation data
        crypto_pairs = ['BTC', 'ETH', 'SOL', 'XRP']
        forex_pairs = ['EUR', 'GBP', 'JPY', 'USD']

        new_is_crypto = any(c in new_symbol for c in crypto_pairs)
        new_is_forex = any(f in new_symbol for f in forex_pairs)

        crypto_count = 0
        forex_count = 0

        for pos in positions:
            symbol = pos.get('symbol', '')
            if any(c in symbol for c in crypto_pairs):
                crypto_count += 1
            if any(f in symbol for f in forex_pairs):
                forex_count += 1

        if new_is_crypto:
            total = crypto_count + forex_count
            if total > 0:
                correlation = crypto_count / total
                if correlation > self.max_correlation:
                    return {
                        'safe': False,
                        'reason': f'High correlation: {correlation:.0%} crypto exposure'
                    }

        if new_is_forex:
            total = crypto_count + forex_count
            if total > 0:
                correlation = forex_count / total
                if correlation > self.max_correlation:
                    return {
                        'safe': False,
                        'reason': f'High correlation: {correlation:.0%} forex exposure'
                    }

        return {'safe': True}

    def update_daily_loss(self, pnl: float, balance: float):
        """Update daily loss tracking"""
        if balance > 0:
            pnl_percent = (pnl / balance) * 100
            self.daily_loss += pnl_percent
            self.daily_trades += 1

            logger.info(f"Daily P&L: {self.daily_loss:.2f}%, Trades: {self.daily_trades}")

    def reset_daily(self):
        """Reset daily tracking"""
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.last_reset = None

    def update_positions_count(self, count: int):
        """Update open positions count"""
        self.open_positions = count

    def get_risk_metrics(self, balance: float) -> Dict[str, Any]:
        """Get current risk metrics"""
        return {
            'daily_loss': self.daily_loss,
            'daily_loss_limit': self.max_daily_loss,
            'daily_trades': self.daily_trades,
            'open_positions': self.open_positions,
            'max_positions': self.max_positions,
            'risk_per_trade': self.max_risk_per_trade,
            'available_risk': max(0, self.max_daily_loss - abs(self.daily_loss)),
            'balance': balance
        }

    def should_stop_trading(self) -> bool:
        """Check if trading should be stopped"""
        if self.daily_loss <= -self.max_daily_loss:
            logger.warning("🚨 Daily loss limit reached - stopping trading")
            return True
        return False
